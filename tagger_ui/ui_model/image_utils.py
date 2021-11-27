""" Some image utility helper function"""
from typing import Union

from PIL import Image

import src.model as model


def calculateImageScale(image: Image.Image, targetSize: model.Size2d) -> float:
    """For the given image, calculate and return the largest scaling factor
    that we can use to fit the image within the given width,height limitations
    while keeping the same image aspect ratio.
    """
    if image is None:
        return 1.0
    if image.width == 0 or image.height == 0:
        return 1.0

    border = 0
    width, height = targetSize.width, targetSize.height
    scaleX: float = 1.0 if image.width < width else width / (image.width + border)
    scaleY: float = 1.0 if image.height < height else height / (image.height + border)
    scale: float = min(
        scaleX, scaleY
    )  # Take the smaller scale and use it for both dimmensions
    return scale


def isAlreadyScaledCorrectly(
    image: Union[Image.Image, None], targetSize: model.Size2d
) -> bool:
    """Determines if the given image is already scaled appropriate for the given
    target size window.
    """
    # If there's no image at all, then it's definitely not scaled correctly
    if image is None:
        return False

    # Test if we're very close to the correct size in at least 1 dimensions
    widthOkay: bool = abs(image.width - targetSize.width) < 2
    heightOkay: bool = abs(image.height - targetSize.height) < 2
    return widthOkay or heightOkay


def scaleImage(image: Image.Image, scale: float) -> Image.Image:
    """Scale the given image with the given scaling factor and return a new image"""
    targetWidth: int = int(image.width * scale)
    targetHeight: int = int(image.height * scale)
    scaledImage = image.resize((targetWidth, targetHeight), Image.ANTIALIAS)
    return scaledImage
