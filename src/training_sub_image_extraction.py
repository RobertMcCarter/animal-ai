import cv2 as cv
import os
from pathlib import Path
from typing import Any, Callable

from . import model
from . import sub_image_regions as sir

print(f"OpenCV version: {cv.__version__}")


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size(IMAGE_WIDTH, IMAGE_HEIGHT)


def createOutputFilePath(output_folder:str, image_info: model.ImageInfo, tag: model.TaggedRegion) -> str:
    """Creates the complete output file path for the given tagged region

    Args:
        output_folder (str): The output folder where we want to save the sub-images
        image_info (model.ImageInfo): The original input image
        tag (model.TaggedRegion): The tag result

    Returns:
        str: The new complete output file path
    """
    path = Path(image_info.filePath)
    sub_folder = "true" if tag else "false"

    # Pad the x/y dimension to keep the images sort of sorted
    x = str(tag.x).zfill(4)
    y = str(tag.y).zfill(4)

    # Now we can build the complete output file path (including the file name and ext)
    dest_file_name = f"{path.stem}_{x}x{y}{path.suffix}"
    result = os.path.join(output_folder, sub_folder, dest_file_name)
    return result


def breakUpImageIntoTaggedSubImages(
    image_info: model.ImageInfo,
    processSubImage: Callable[[model.ImageInfo, model.TaggedRegion, Any], None],
    block_size: model.Size = BLOCK_SIZE,
) -> None:
    """Break up the given `image` into `block_size` sized sub-images and save them to the
    given `outputFolder` based on the sub-image tag value.

    Args:
        image_info (model.ImageInfo): The original large image information to break-up
            into smaller pieces
            (this is the image that will be loaded into memory and cut up)
        block_size (model.Size): The target size for the smaller sub-images
        processSubImage (Callable[[model.ImageInfo, Any], None]): The function that will be passed
        image info the sub image
    """
    assert image_info is not None
    assert processSubImage is not None
    assert block_size is not None

    # Load the image
    image: Any = cv.imread(image_info.filePath)

    height, width = image.shape[0], image.shape[1]
    image_size = model.Size(width, height)

    # Create the sub-regions that we need to break the large image into
    sub_image_regions = sir.createSubImageRegions(block_size, image_size)
    sub_image_tagged_regions = sir.createSubImageTaggedRegions(
        sub_image_regions, image.regions
    )

    for sr in sub_image_tagged_regions:
        # Numpy uses row, col notation instead of col, row
        # From: https://stackoverflow.com/questions/67353650/extract-part-of-a-image-using-opencv
        # or: https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
        # or: https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
        sub_image = image[sr.y1 : sr.y2, sr.x1 : sr.x2]
        processSubImage(image_info, sr, sub_image)


def saveTaggedSubImage(
    outputFolder: str, image_info: model.ImageInfo, sub_image: Any
) -> None:
    pass


def saveUntaggedSubImage(
    outputFolder: str, image_info: model.ImageInfo, sub_image: Any
) -> None:
    pass


def saveSubImages(
    image_info: model.ImageInfo,
    outputFolder: str,
    block_size: model.Size = BLOCK_SIZE,
) -> None:
    assert image_info is not None
    assert block_size is not None
    assert os.path.isdir(outputFolder)
    assert os.path.isdir(os.path.join(outputFolder, "true"))
    assert os.path.isdir(os.path.join(outputFolder, "false"))
