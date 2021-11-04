import cv2 as cv
import os

import model
import sub_image_regions as sir

print(f"OpenCV version: {cv.__version__}")


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size(IMAGE_WIDTH, IMAGE_HEIGHT)


def breakUpImage(
    image: model.ImageInfo, outputFolder: str, block_size: model.Size = BLOCK_SIZE
) -> None:
    """Break up the given `image` into `block_size` sized sub-images and save them to the
    given `outputFolder` based on the sub-image tag value.

    Args:
        image (model.ImageInfo): The original large image to break-up into smaller pieces
        block_size (model.Size): The target size for the smaller sub-images
        outputFolder (str): The output folder for the tagged images
    """
    assert image is not None
    assert block_size is not None
    assert outputFolder is not None and not outputFolder.isspace()
    assert os.path.isdir(outputFolder)
    assert os.path.isdir(os.path.join(outputFolder, "true"))
    assert os.path.isdir(os.path.join(outputFolder, "false"))

    # Load the image
    large_image = cv.imread(image.filePath)
    height, width = large_image.shape[0], large_image.shape[1]
    image_size = model.Size(width, height)

    # Create the sub-regions that we need to break the large image into
    sub_image_regions = sir.createSubImageRegions(block_size, image_size)
    sub_image_tagged_regions = sir.createSubImageTaggedRegions(sub_image_regions, image.regions )

    for sub_region in sub_image_tagged_regions:
        pass



# Numpy uses row, col notation instead of col, row
# From: https://stackoverflow.com/questions/67353650/extract-part-of-a-image-using-opencv
# or: https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
# or: https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
# `crop_img = img[y:y+h, x:x+w]`

# Aternatively, if you have defined a crop margin, you can do
# crop_img = img[margin:-margin, margin:-margin] –

