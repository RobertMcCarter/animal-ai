# Contains functions for loading and saving JSON to and from our model classes
import glob
import io
import os
import asyncio
import json

from typing import Dict, List, Union

from PIL import Image
import aiofiles

import model
from model.region2d import ScaledRegion2d


# ##################################################################################################
# region Functions dealing with loading images
# ##################################################################################################

async def loadImage( filePath:str ) -> Image.Image:
    """ Load the given image and return it asynchronously
    """
    # See: https://github.com/Tinche/aiofiles
    async with aiofiles.open(filePath, mode='rb') as f:
        # See: https://www.delftstack.com/howto/python/read-binary-files-in-python/
        buffer = await f.read()

        # See: https://pillow.readthedocs.io/en/stable/handbook/tutorial.html#more-on-reading-images
        image = Image.open( io.BytesIO(buffer) )
        return image


async def loadImageForAnnotation( aimage:model.AnnotatedImage ):
    """ Load the given image and return it asynchronously
    """
    # See: https://github.com/Tinche/aiofiles
    if aimage.image is None:
        aimage.image = await loadImage(aimage.filePath)


async def loadNearbyImages( annotatedImages:List[model.AnnotatedImage],
                            index:int,
                            targetSize: model.Size2d,
                            previous:int=2, next:int=5 ) -> None:
    """ Asynchronously pre-loads nearby images (if they're not already loaded).
        This is done to ensure a snappy UI when the user is switching
        quickly between images.
    """
    # First, figure out our range
    startIndex = max(0, index - previous)
    endIndex = min(index + next, len(annotatedImages)-1)

    # Load all of the images we're interestd in
    tasks: List[asyncio.Task] = []
    for i in range(startIndex, endIndex):
        aimage = annotatedImages[i]
        if aimage.image is None:
            task = asyncio.create_task(loadImageForAnnotation(aimage) )
            tasks.append( task )

    # Wait for all of the loading tasks to complete
    for task in tasks:
        await task

    # Clear out images outside our range
    for i in range(0, startIndex):
        annotatedImages[i].image = None
    for i in range(endIndex + 1, len(annotatedImages) ):
        annotatedImages[i].image = None

# endregion


# ##################################################################################################
# region Functions to (de)serialize a Region2d
# ##################################################################################################

def serializeRegion2dToDict( region: model.Region2d ) -> Dict:
    """ Serialize a Region2d into a Dict suitable for saving to JSON.
    """
    nr = region.normalize()
    return {
        'x': nr.x,
        'y': nr.y,
        'w': nr.w,
        'h': nr.h
    }

def deSerializeRegion2d( data: Dict ) -> model.Region2d:
    """ Serialize a JSON dictionary back into a Region2d.
    """
    return model.Region2d(
        data['x'],
        data['y'],
        data['w'],
        data['h']
    )

# endregion


# ##################################################################################################
# region Functions to (de)serialize an AnnotatedImage
# ##################################################################################################

def serializeAnnotatedImageToDict( image: model.AnnotatedImage ) -> Dict:
    """ Convert an annotated image into a JSON dictionary
    """
    return {
        'tagged': image.isTagged,
        'filePath': image.filePath,
        'regions': [
            serializeRegion2dToDict(r.imageRegion) for r in image.regions
                                        if r.imageRegion is not None
        ]
    }


def deSerializeAnnotatedImage( data: Dict ) -> model.AnnotatedImage:
    """ Convert an annotated image into a JSON dictionary
    """
    result = model.AnnotatedImage(data['filePath'])
    result.isTagged = data['tagged']
    if 'regions' in data:
        for regionDict in data['regions']:
            region = deSerializeRegion2d(regionDict)
            scaledRegion= ScaledRegion2d(None, region)
            result.addRegion(scaledRegion)

    return result

# endregion


# ##################################################################################################
# region Functions to (de)serialize a Region2d
# ##################################################################################################

def serializeAnnotatedImagesToDict( manager: model.AnnotatedImagesManager ) -> Dict:
    """ Convert a list of annotated images to JSON for serialization
    """
    return {
        'maxViewed': manager.maxViewed,
        'images': [ serializeAnnotatedImageToDict(image) for image in manager.images ]
    }


def deSerializeAnnotatedImages( data: Dict ) -> model.AnnotatedImagesManager:
    """ Convert a previously serialized annotated images manager JSON dictionary
        back into an in-memory AnnotatedImagesManager
    """
    annotatedImages = [ deSerializeAnnotatedImage(ai) for ai in data['images']]
    manager = model.AnnotatedImagesManager(annotatedImages)
    manager.maxViewed = data['maxViewed']
    manager.moveToImage(manager.maxViewed)
    return manager


DIR_ANNOTATIONS_FILE_NAME = "__annotations.json"


def saveAnnotatedImagesToJson( manager: model.AnnotatedImagesManager ) -> None:
    """ Saves the given collection of annotated images to the directory file
    """
    assert manager
    assert manager.saveFileName

    # First, we turn our annotated images manager into a dictionary with just the data
    # we actually want to persist
    data = serializeAnnotatedImagesToDict(manager)

    # Now we can save that data
    with open(manager.saveFileName, "w") as file:
        json.dump(data, file, indent=2)


def createAnnotatedImagesFromDirectory(directory:str) -> List[model.AnnotatedImage]:
    """Create annotated image objects for all the images in the given directory
       (enumerates the images in the directory to create this list;
        this function does NOT use the DIR_ANNOTATIONS_FILE_NAME JSON file)
    """
    fileTypes = ('*.png', '*.jpg')
    fileNames = []
    for ext in fileTypes:
        globPath = os.path.join(directory,ext)
        newFileNames = glob.glob(globPath)
        newFileNames = [ f.replace("\\","/") for f in newFileNames ]
        fileNames.extend(newFileNames)

    fileNames.sort()
    annotatedImages = [ model.AnnotatedImage(f) for f in fileNames ]
    return annotatedImages


def loadDirectoryFromFiles(directory:str) -> model.AnnotatedImagesManager:
    """Create annotated image manager for all the images in the given directory
       by enumerating the images
       (this function does NOT use the DIR_ANNOTATIONS_FILE_NAME JSON file)
    """
    annotatedImages = createAnnotatedImagesFromDirectory(directory)
    manager = model.AnnotatedImagesManager(annotatedImages)
    manager.saveFileName = os.path.join(directory, DIR_ANNOTATIONS_FILE_NAME)
    return manager


def loadImageListFromJsonFile( fileName: str, windowSize: model.Size2d ) -> Union[ model.AnnotatedImagesManager, None]:
    """ Loads the given json file
        (if it doesn't exist, this function returns None)
    """
    assert fileName

    # Test if the JSON file exists (if not, return None)
    exists: bool = os.path.isfile(fileName)
    if not exists: return None

    # It does, try and load it
    try:
        with open(fileName, 'r') as file:
            data: Dict = json.load(file)
            manager = deSerializeAnnotatedImages(data)
            manager.saveFileName = fileName
            manager.onWindowResized(windowSize)
            return manager
    except Exception as e:
        print("Failed to read JSON file:" + str(e))
        return None


def loadDirectory( directory: str, windowSize: model.Size2d ) -> model.AnnotatedImagesManager:
    """ Return an annotated images manager,
        loaded with the images from the given directory
    """
    assert directory

    # First, try and load the directory using any previously saved JSON file
    jsonDirFileName: str = os.path.join(directory, DIR_ANNOTATIONS_FILE_NAME)
    manager = loadImageListFromJsonFile(jsonDirFileName, windowSize)
    if manager is not None:
        return manager

    # If that didn't work, load the images directly from the list of images
    manager = loadDirectoryFromFiles(directory)
    if manager is not None:
        manager.onWindowResized(windowSize)
    return manager

# endregion
