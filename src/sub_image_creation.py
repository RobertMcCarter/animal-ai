import cv2 as cv
from typing import Iterable, List

import model

print(f"OpenCV version: {cv.__version__}")


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH  = 128
IMAGE_HEIGHT = 128


def createSubImageOffsets( block_size:int, image_size: int ) -> Iterable[int]:
    """ Create the list of x-offsets within a larger image where we should extract
        smaller sub-images.
        This function is generic, and can be used for either the x or y offsets.
        This sounds like it should be trivial, and it mostly is except for the
        last bit, where the last square to select from the image may not line up with the
        right hand side of the image (but we don't want to leave pixels left unused).
        In that case, this returns `image_size - block_size` as the last offset,
        which will cause some pixels to appear in both the last and second last extracted
        sub-image (but that should be okay.)

    Args:
        block_size (int): The size of the smaller image (either the width or the height)
                          that will be extracted from the larger image.

        image_size (int): The size of the larger image
                          (either the width or the height of the image).

    Returns:
        List[int]: The collection of offsets all the smaller images to extract
    """
    assert( block_size < image_size )

    endRange = image_size - (image_size % block_size)
    for i in range(0, endRange, block_size):
        yield i

    # Optional last entry if left over pixels
    if image_size % block_size > 0:
        yield image_size - block_size


def createSubImageRegions( block_size: model.Size, image_size: model.Size ) -> Iterable[model.Region]:
    """ Create all of the sub-regions within the main image that should be extracted
        to create our data suitable for input into the AI image tester or for training.

    Args:
        block_size (model.Size): The smaller image sizes that we'll extract from the larger image
        image_size (model.Size): The larger image size that we're extracting from

    Returns:
        List[model.Region]: All of the region within the larger image to extract
    """
    assert( block_size.width < image_size.width )
    assert( block_size.height < image_size.height )

    # Grab all the offsets once (and turn them into lists, we'll reuse them)
    xOffsets = list( createSubImageOffsets(block_size.width, image_size.width ) )
    yOffsets = list( createSubImageOffsets(block_size.height, image_size.height) )

    # Convert our offsets into regions
    for y in yOffsets:
        for x in xOffsets:
            yield model.Region(x=x, y=y, w=block_size.width, h=block_size.height)


def createSubImageTaggedRegions(
            block_size: model.Size,
            image_size: model.Size,
            tagged_regions: List[model.Region] ) -> Iterable[model.TaggedRegion]:
    """ Generates the various regions (and tags them) that need to be extracted from image2,
        tagged and saved as training images.

    Args:
        image1 (model.ImageInfo): The first image information in the pair
        image2 (model.ImageInfo): The second image information in the pair of images
        imageDim (model.Dimension): The size of both images (they must be equal)

    Returns:
        List[model.TaggedRegion]: A list of tagged regions for image 2 that should be
            extracted and saved as training data.
    """
    sub_image_regions = createSubImageRegions(block_size, image_size)
    for r in sub_image_regions:
        tagged = model.intersectsAny( r, tagged_regions )
        yield model.TaggedRegion(x=r.x, y=r.y, w=r.w, h=r.h, tag=tagged)
