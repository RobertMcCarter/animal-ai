#!python
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
"""
This is the final pre-training application that takes the original images
and cuts them into 224x224 sub-images, saving the tens of thousands
of sub-images into `true` and `false` sub-folders according to the
tagging data from `animals.json`
"""
from dataclasses import dataclass
import cv2
import random
import os
from PIL import Image as pilImage
import piexif
from pathlib import Path
from typing import Any, Callable, Union

from src import model
from src import data_serialization_json as ds
from src import grouping
from src import sub_image_regions as sir
from tagger_ui.ui_model.timer import Timer

print(f"OpenCV version: {cv2.__version__}")

# The image output directory
out_dir = r"D:\data\NRSI\__ai_training_images"

# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
BLOCK_SIZE = model.Size2d(IMAGE_WIDTH, IMAGE_HEIGHT)


def createOutputFilePath(
    out_dir: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion2d,
    rotation: str = "",
) -> str:
    """Creates the complete output file path for the given tagged region

    Args:
        out_dir (str): The output folder where we want to save the sub-images
        image_info (model.ImageInfo): The original input image
        region (model.TaggedRegion): The tag result

    Returns:
        str: The new complete output file path
    """
    path = Path(image_info.filePath)
    sub_folder = "true" if region.tag else "false"

    # Pad the x/y dimension to keep the images sort of sorted
    x = str(region.x).zfill(4)
    y = str(region.y).zfill(4)

    # Now we can build the complete output file path (including the file name and ext)
    if rotation:
        rotation = "_" + rotation
    dest_file_name = f"{path.stem}_@{x}x{y}{rotation}{path.suffix}"
    result = os.path.join(out_dir, sub_folder, dest_file_name)
    return result


# The callable (function) type that the `breakUpImageIntoTaggedSubImages` function
# uses to save either positive or negatively tagged images
SaveSubImageFn = Callable[[str, model.ImageInfo, model.TaggedRegion2d, Any], None]


def saveTaggedSubImage(
    out_dir: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion2d,
    sub_image: Any,
) -> None:
    """Save a positively tagged sub-image
    In the future this function will likely flip horizontally (and possibly vertically as well)
    to increase the number of positively tagged images.

    Args:
        out_dir (str): The top-level output folder
        image_info (model.ImageInfo): The original large image information
        region (model.TaggedRegion): The tagged information about the sub-image being saved
        sub_image (Any): The actual sub-image data
    """
    output_file = createOutputFilePath(out_dir, image_info, region)
    cv2.imwrite(output_file, sub_image)


def saveUntaggedSubImage(
    out_dir: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion2d,
    sub_image: Any,
) -> None:
    """Save a sub-image that was tagged False
    In the future this function will likely flip horizontally (and possibly vertically as well)
    to increase the number of positively tagged images.

    Args:
        out_dir (str): The top-level output folder
        image_info (model.ImageInfo): The original large image information
        region (model.TaggedRegion): The tagged information about the sub-image being saved
        sub_image (Any): The actual sub-image data
    """
    output_file = createOutputFilePath(out_dir, image_info, region)
    cv2.imwrite(output_file, sub_image)


def create_image_exif_metadata(image_info: model.ImageInfo) -> bytes:
    """Create basic image EXIF metadata for the given image information.

    Args:
        image_info (model.ImageInfo): The original image path is saved into the EXIF metadata

    Returns:
        [type]: The byte array containing the encoded EXIF metadata
    """
    zeroth_ifd = {
        piexif.ImageIFD.Make: "Stealth Cam",  # NSCI seems to use this brand of camera
        piexif.ImageIFD.Software: "animal-ai",  # This software!
    }
    first_ifd = {}
    exif_ifd = {
        piexif.ExifIFD.ImageUniqueID: image_info.filePath,
    }
    gps_ifd = {}

    # exif_dict = {"Exif":exif_ifd }
    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": gps_ifd,
        "1st": first_ifd,
    }
    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes


def create_directory_if_not_exists(dir: str) -> None:
    """Create the given directory if it doesn't already exist

    Args:
        dir (str): The full path to the directory to create
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


@dataclass(frozen=True)
class OutputImageInfo:
    """The required information to save a resulting sub-image"""

    out_dir: str
    image_info: model.ImageInfo
    sub_region: model.TaggedRegion2d


def save_sub_image(
    output_info: OutputImageInfo, sub_image_diff: Any, rotation: str = ""
) -> None:
    """Saves a sub-image

    Args:
        out_dir (str): The top-level output folder where we're saving all sub-images
        image_info (model.ImageInfo): The original main image information (for the file name)
        sub_region (model.TaggedRegion2d): The tagged region within the main image where
            this sub-image is being taken from
        sub_image_diff (Any): The actual sub-image pre-calculated diff to save
        rotation (str): The optional rotational information for the output file name
    """
    assert output_info

    # Determine which folder to save the file in
    output_file = createOutputFilePath(
        output_info.out_dir, output_info.image_info, output_info.sub_region, rotation
    )

    # Create the image metadata (which contains the original image source file path)
    exif_metadata_bytes = create_image_exif_metadata(output_info.image_info)

    # Create a PIL/Pillow image from our OpenCV2 image (so that we can save it with metadata)
    pillow_image = pilImage.fromarray(sub_image_diff)
    pillow_image.save(output_file, format="JPEG", exif=exif_metadata_bytes)
    # cv2.imwrite(output_file, sub_image_diff)   # Can't save metadata with OpenCV2


def save_sub_image_tagged_true(
    output_info: OutputImageInfo, sub_image_diff: Any
) -> None:
    """
    Saves a positively (true) tagged sub-image.
    To generate more positive examples this function also saves copies of the sub-region
    flipped and roated in various ways.

    See:
        https://note.nkmk.me/en/python-opencv-numpy-rotate-flip

    Args:
        out_dir (str): The top-level output folder where we're saving all sub-images
        image_info (model.ImageInfo): The original main image information (for the file name)
        sub_region (model.TaggedRegion2d): The tagged region within the main image where
            this sub-image is being taken from
        sub_image_diff (Any): The actual sub-image pre-calculated diff to save
    """
    # First save the original image
    save_sub_image(output_info, sub_image_diff)

    # Rotate the image 90° clockwise
    img_rotate_90_c = cv2.rotate(sub_image_diff, cv2.ROTATE_90_CLOCKWISE)
    save_sub_image(output_info, img_rotate_90_c, "rotate_90°c")

    # Rotate the image 90° counter-clockwise
    img_rotate_90_cc = cv2.rotate(sub_image_diff, cv2.ROTATE_90_COUNTERCLOCKWISE)
    save_sub_image(output_info, img_rotate_90_cc, "rotate_90°cc")

    # Same as flipping in both x and y axis
    # img_rotate_180 = cv2.rotate(sub_image_diff, cv2.ROTATE_180)
    # save_sub_image(output_info, img_rotate_180, "rotate_180°")

    # Flip the image along the x axis
    img_flip_x = cv2.flip(sub_image_diff, 1)  # > 0 is flip horizontally
    save_sub_image(output_info, img_flip_x, "flipped_x")

    # Flip the image along the y axis
    img_flip_y = cv2.flip(sub_image_diff, 0)  # = 0 is flip vertically
    save_sub_image(output_info, img_flip_y, "flipped_y")

    # Flip the image along both the x and y axis
    img_flip_xy = cv2.flip(sub_image_diff, -1)  # < 0 is flip both x and y
    save_sub_image(output_info, img_flip_xy, "flipped_xy")


def save_sub_image_tagged_false(
    output_info: OutputImageInfo,
    sub_image_diff: Any,
) -> None:
    """
    Saves a positively (true) tagged sub-image.
    To generate fewer negative examples for AI training this function may or may not
    save the given sub-image.

    Currently it only has a 7.5% chance of actually saving the negative example

    Args:
        out_dir (str): The top-level output folder where we're saving all sub-images
        image_info (model.ImageInfo): The original main image information (for the file name)
        sub_region (model.TaggedRegion2d): The tagged region within the main image where
            this sub-image is being taken from
        sub_image_diff (Any): The actual sub-image pre-calculated diff to save
    """
    value: float = random.random()
    if value < 0.075:
        save_sub_image(output_info, sub_image_diff)


def main():
    """Process the main images `.json` data file to create 224x224 training sub-images."""

    # Load the list of animals from the animals JSON file
    images_data_file: model.ImagesCollection = ds.loadImagesCollectionFromJson(
        "animals.json"
    )

    # Group them
    image_groups: list[list[model.ImageInfo]] = grouping.groupImages(
        images_data_file.images
    )

    # Where we will save the 128x128 training images - create true/false sub dirs if required
    print("Output folder: ", out_dir)
    create_directory_if_not_exists(out_dir)
    create_directory_if_not_exists(os.path.join(out_dir, "true"))
    create_directory_if_not_exists(os.path.join(out_dir, "false"))

    # For every group
    group_count = 0
    for animal_group in image_groups:
        # For each group we want to track the previous
        group_count += 1
        print(f"Group #{group_count} of {len(image_groups)}")
        previous_image: Union[Any, None] = None
        for image_info in animal_group:
            # Load the image and grab its dimensions
            current_image: Any = cv2.imread(image_info.filePath)
            height, width = current_image.shape[0], current_image.shape[1]
            image_size = model.Size2d(width, height)

            # Check that we have a previous image to operate on
            if previous_image is None:
                previous_image = current_image
                continue

            # Check that the current image is the same shape as the previous image
            # (for some reason the images are sometimes different shapes)
            if previous_image.shape != current_image.shape:
                print("Different image sizes - skipping")
                previous_image = current_image
                continue

            # Calculate the difference with the previous image
            print("Processing: ", image_info.filePath)
            image_diff = current_image - previous_image

            # Create the sub-regions that we need to break the large image into
            sub_image_regions = sir.createSubImageRegions(BLOCK_SIZE, image_size)
            sub_image_tagged_regions = sir.createSubImageTaggedRegions(
                sub_image_regions, image_info.regions
            )

            # Loop over each sub-image region
            for sub_region in sub_image_tagged_regions:
                # Numpy uses row, col notation instead of col, row
                # From: https://stackoverflow.com/questions/67353650/extract-part-of-a-image-using-opencv
                # or: https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
                # or: https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
                sub_image_diff = image_diff[
                    sub_region.y1 : sub_region.y2, sub_region.x1 : sub_region.x2
                ]

                output_info = OutputImageInfo(out_dir, image_info, sub_region)
                if sub_region.tag:
                    save_sub_image_tagged_true(output_info, sub_image_diff)
                else:
                    save_sub_image_tagged_false(output_info, sub_image_diff)

            # Update the previous image for the next image subtraction
            previous_image = current_image


if __name__ == "__main__":
    with Timer("Extract tagged sub-images"):
        main()
