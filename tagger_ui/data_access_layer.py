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


def convertImageInfoToAnnotatedImage(
    image_info: model.ImageInfo,
) -> uiModel.AnnotatedImage:
    """Convert an image info object into a view model AnnotatedImage object"""
    assert image_info

    result = uiModel.AnnotatedImage(image_info.filePath)
    result.isTagged = image_info.tagged
    for region in image_info.regions:
        scaledRegion = uiModel.ScaledRegion2d(None, region)
        result.addRegion(scaledRegion)
    return result


def convertAnnotatedImageToImageInfo(ai: uiModel.AnnotatedImage) -> model.ImageInfo:
    """Convert an AnnotatedImage object into a core model ImageInfo object for saving"""
    assert ai

    regions: list[model.Region2d] = [
        r.imageRegion for r in ai.regions if r.imageRegion is not None
    ]
    result = model.ImageInfo(ai.isTagged, ai.filePath, regions)
    return result


def convertImagesCollectionToAnnotatedImagesManager(
    collection: model.ImagesCollection,
) -> uiModel.AnnotatedImagesManager:
    """Convert a core model images collection into the view model layer
    annotated images manager (which has more logic for our particular UI)
    """
    assert collection

    annotatedImages = [
        convertImageInfoToAnnotatedImage(info) for info in collection.images
    ]
    manager = uiModel.AnnotatedImagesManager(annotatedImages)
    manager.maxViewed = collection.maxViewed
    return manager


def convertAnnotatedImagesManagerToImagesCollection(
    manager: uiModel.AnnotatedImagesManager,
) -> model.ImagesCollection:
    """Convert a UI annotated images manager into a core model images collection for saving"""
    assert manager

    images = [convertAnnotatedImageToImageInfo(i) for i in manager.images]
    collection = model.ImagesCollection(manager.maxViewed, images)
    return collection


def saveAnnotatedImagesToJsonFile(
    file_name: str, manager: uiModel.AnnotatedImagesManager
) -> None:
    """Saves the given collection of annotated images to the same"""
    assert manager
    assert file_name

    collection = convertAnnotatedImagesManagerToImagesCollection(manager)
    json_serializer.saveImagesCollectionToJson(file_name, collection)


def loadAnnotatedImagesFromJsonFile(
    file_name: str,
) -> uiModel.AnnotatedImagesManager:
    """Loads the given json file (if it doesn't exist, this function returns None)"""
    assert file_name
    exists: bool = os.path.isfile(file_name)
    if not exists:
        raise FileNotFoundError()

    # The .json file exists, so we'll try and load it into a
    # view model style annotated images manager
    collection = json_serializer.loadImagesCollectionFromJson(file_name)
    manager = convertImagesCollectionToAnnotatedImagesManager(collection)
    manager.saveFileName = file_name
    return manager


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


def loadDirectory(directory: str) -> uiModel.AnnotatedImagesManager:
    """Return an annotated images manager,
    loaded with the images from the given directory
    """
    assert directory

    # First, try and load the directory using any previously saved JSON file
    jsonDirFileName: str = os.path.join(directory, DIR_ANNOTATIONS_FILE_NAME)
    manager = loadAnnotatedImagesFromJsonFile(jsonDirFileName)
    if manager is not None:
        return manager

    # If that didn't work, load the images directly from the list of images
    manager = loadDirectoryFromFiles(directory)
    return manager


# endregion
