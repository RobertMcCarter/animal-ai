import cv2 as cv
import os
from PIL import Image as pilImage
import piexif
from pathlib import Path
from typing import Any, Callable

from src import model
from src import data_serialization_json as ds
from src import grouping
from src import sub_image_regions as sir

print(f"OpenCV version: {cv.__version__}")


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size2d(IMAGE_WIDTH, IMAGE_HEIGHT)


def createOutputFilePath(
    output_folder: str, image_info: model.ImageInfo, region: model.TaggedRegion2d
) -> str:
    """Creates the complete output file path for the given tagged region

    Args:
        output_folder (str): The output folder where we want to save the sub-images
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
    dest_file_name = f"{path.stem}_@{x}x{y}{path.suffix}"
    result = os.path.join(output_folder, sub_folder, dest_file_name)
    return result


# The callable (function) type that the `breakUpImageIntoTaggedSubImages` function
# uses to save either positive or negatively tagged images
SaveSubImageFn = Callable[[str, model.ImageInfo, model.TaggedRegion2d, Any], None]


def saveTaggedSubImage(
    output_folder: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion2d,
    sub_image: Any,
) -> None:
    """Save a positively tagged sub-image
    In the future this function will likely flip horizontally (and possibly vertically as well)
    to increase the number of positively tagged images.

    Args:
        output_folder (str): The top-level output folder
        image_info (model.ImageInfo): The original large image information
        region (model.TaggedRegion): The tagged information about the sub-image being saved
        sub_image (Any): The actual sub-image data
    """
    output_file = createOutputFilePath(output_folder, image_info, region)
    cv.imwrite(output_file, sub_image)


def saveUntaggedSubImage(
    output_folder: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion2d,
    sub_image: Any,
) -> None:
    """Save a sub-image that was tagged False
    In the future this function will likely flip horizontally (and possibly vertically as well)
    to increase the number of positively tagged images.

    Args:
        output_folder (str): The top-level output folder
        image_info (model.ImageInfo): The original large image information
        region (model.TaggedRegion): The tagged information about the sub-image being saved
        sub_image (Any): The actual sub-image data
    """
    output_file = createOutputFilePath(output_folder, image_info, region)
    cv.imwrite(output_file, sub_image)


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


def create_directory(dir: str) -> None:
    """Create the given directory if it doesn't already exist

    Args:
        dir (str): The full path to the directory to create
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def main():
    """Process the main images `.json` data file to create 128x128 training sub-images."""

    # Load the list of animals from the animals JSON file
    images_data_file: model.ImagesCollection = ds.loadImagesCollectionFromJson(
        "animals.json"
    )

    # Group them
    image_groups: list[list[model.ImageInfo]] = grouping.groupImages(
        images_data_file.images
    )

    # Where we will save the 128x128 training images - create true/false sub dirs if required
    output_folder = r"D:\data\NRSI\__ai_training_images"
    print("Output folder: ", output_folder)
    create_directory(os.path.join(output_folder, "true"))
    create_directory(os.path.join(output_folder, "false"))

    # For every group
    group_count = 0
    for animal_group in image_groups:
        # For each group we want to track the previous
        group_count += 1
        print("Group #", group_count)
        previous_image: Any | None = None
        for image_info in animal_group:
            # Load the image and grab its dimensions
            current_image: Any = cv.imread(image_info.filePath)
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

                # Determine which folder to save the file in
                output_file = createOutputFilePath(
                    output_folder, image_info, sub_region
                )

                # Create the image metadata (which contains the original image source file path)
                exif_metadata_bytes = create_image_exif_metadata(image_info)

                # Create a PIL/Pillow image from our OpenCV2 image (so that we can save it with metadata)
                pillow_image = pilImage.fromarray(sub_image_diff)
                pillow_image.save(output_file, format="JPEG", exif=exif_metadata_bytes)
                # cv.imwrite(output_file, sub_image_diff)   # Can't save metadata with OpenCV2

            # Update the previous image for the next image subtraction
            previous_image = current_image


if __name__ == "__main__":
    main()
