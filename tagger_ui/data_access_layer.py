# Contains functions for loading and saving JSON to and from our model classes
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
import glob
import os

import src.model as model
import tagger_ui.ui_model as uiModel

import src.data_serialization_json as json_serializer


DIR_ANNOTATIONS_FILE_NAME = "__annotations.json"


# #################################################################################################
# Convert the core src.model data structures into more view model like data structures
# required by the TK UI
# #################################################################################################


def convertImageInfoToViewModel(imageInfo: model.ImageInfo) -> uiModel.AnnotatedImage:
    """Convert an image info object into a view model AnnotatedImage object"""
    assert imageInfo
    result = uiModel.AnnotatedImage(imageInfo.filePath)
    result.isTagged = imageInfo.tagged
    for region in imageInfo.regions:
        scaledRegion = uiModel.ScaledRegion2d(None, region)
        result.addRegion(scaledRegion)
    return result


def convertImagesCollectionToViewModel(
    collection: model.ImagesCollection,
) -> uiModel.AnnotatedImagesManager:
    """Convert a core model images collection into the view model layer
    annotated images manager (which has more logic for our particular UI)
    """
    assert collection
    annotatedImages = [convertImageInfoToViewModel(info) for info in collection.images]
    manager = uiModel.AnnotatedImagesManager(annotatedImages)
    manager.maxViewed = collection.maxViewed
    return manager


def loadImageCollectionJsonFile(
    file_name: str, windowSize: uiModel.Size2d
) -> uiModel.AnnotatedImagesManager | None:
    """Loads the given json file (if it doesn't exist, this function returns None)

    NOTE:  This function can ONLY be called if there is a main Tk window created.
    (which makes it hard to unit test)
    """
    # Check pre-conditions
    assert file_name
    exists: bool = os.path.isfile(file_name)
    if not exists:
        return None

    # The .json file exists, so we'll try and load it into a
    # view model style annotated images manager
    try:
        collection = json_serializer.loadImagesCollectionFromJson(file_name)
        manager = convertImagesCollectionToViewModel(collection)
        manager.moveToImage(manager.maxViewed)  # Requires a Tk window!
        manager.saveFileName = file_name
        manager.onWindowResized(windowSize)     # Also requires a Tk window!
        return manager
    except Exception as e:
        print("Failed to read JSON file:" + str(e))
        return None


def createAnnotatedImagesFromDirectory(directory: str) -> list[uiModel.AnnotatedImage]:
    """Create annotated image objects for all the images in the given directory
    (enumerates the images in the directory to create this list;
     this function does NOT use the DIR_ANNOTATIONS_FILE_NAME JSON file)
    """
    fileTypes = ("*.png", "*.jpg")
    fileNames: list[str] = []
    for ext in fileTypes:
        globPath = os.path.join(directory, ext)
        newFileNames = glob.glob(globPath)
        newFileNames = [f.replace("\\", "/") for f in newFileNames]
        fileNames.extend(newFileNames)

    fileNames.sort()
    annotatedImages = [uiModel.AnnotatedImage(f) for f in fileNames]
    return annotatedImages


def loadDirectoryFromFiles(directory: str) -> uiModel.AnnotatedImagesManager:
    """Create annotated image manager for all the images in the given directory
    by enumerating the images
    (this function does NOT use the DIR_ANNOTATIONS_FILE_NAME JSON file)
    """
    annotatedImages = createAnnotatedImagesFromDirectory(directory)
    manager = uiModel.AnnotatedImagesManager(annotatedImages)
    manager.saveFileName = os.path.join(directory, DIR_ANNOTATIONS_FILE_NAME)
    return manager


def loadDirectory(
    directory: str, windowSize: uiModel.Size2d
) -> uiModel.AnnotatedImagesManager:
    """Return an annotated images manager,
    loaded with the images from the given directory
    """
    assert directory

    # First, try and load the directory using any previously saved JSON file
    jsonDirFileName: str = os.path.join(directory, DIR_ANNOTATIONS_FILE_NAME)
    manager = loadImageCollectionJsonFile(jsonDirFileName, windowSize)
    if manager is not None:
        return manager

    # If that didn't work, load the images directly from the list of images
    manager = loadDirectoryFromFiles(directory)
    if manager is not None:
        manager.onWindowResized(windowSize)
    return manager


# endregion
