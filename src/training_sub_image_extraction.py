import cv2 as cv
import os
from pathlib import Path
from typing import Any, Callable

from src import model
from src import animals_json as aj
from src import grouping
from src import sub_image_regions as sir

print(f"OpenCV version: {cv.__version__}")


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size(IMAGE_WIDTH, IMAGE_HEIGHT)


def createOutputFilePath(
    output_folder: str, image_info: model.ImageInfo, region: model.TaggedRegion
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
    dest_file_name = f"{path.stem}_{x}x{y}{path.suffix}"
    result = os.path.join(output_folder, sub_folder, dest_file_name)
    return result


# The callable (function) type that the `breakUpImageIntoTaggedSubImages` function
# uses to save either positive or negatively tagged images
SaveSubImageFn = Callable[[str, model.ImageInfo, model.TaggedRegion, Any], None]


def saveTaggedSubImage(
    output_folder: str,
    image_info: model.ImageInfo,
    region: model.TaggedRegion,
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
    region: model.TaggedRegion,
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


def main():
    """Process the main images `.json` data file to create 128x128 training sub-images."""

    # Load the list of animals from the animals JSON file
    images_data_file: model.ImagesInfo = aj.loadAnimalsJson("animals.json")

    # Group them
    image_groups: list[list[model.ImageInfo]] = grouping.groupImages(
        images_data_file.images
    )

    # Where we will save the 128x128 training images
    output_folder = r"D:\data\NRSI\__ai_training_images"
    print("Output folder: ", output_folder)

    # For every group
    for animal_group in image_groups:
        # For each group we want to track the previous
        previous_image: Any | None = None
        print("Next group...")
        for image_info in animal_group:
            # Load the image and grab its dimensions
            current_image: Any = cv.imread(image_info.filePath)
            height, width = current_image.shape[0], current_image.shape[1]
            image_size = model.Size(width, height)

            # Calculate the difference with the previous image
            if previous_image is None:
                previous_image = current_image
                continue
            print("Processing: ", image_info.filePath)
            image_diff = current_image - previous_image

            # Create the sub-regions that we need to break the large image into
            sub_image_regions = sir.createSubImageRegions(BLOCK_SIZE, image_size)
            sub_image_tagged_regions = sir.createSubImageTaggedRegions(
                sub_image_regions, image_info.regions
            )

            # Loop over each sub-image region
            for sr in sub_image_tagged_regions:
                # Numpy uses row, col notation instead of col, row
                # From: https://stackoverflow.com/questions/67353650/extract-part-of-a-image-using-opencv
                # or: https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
                # or: https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
                sub_image_diff = image_diff[sr.y1 : sr.y2, sr.x1 : sr.x2]

                # Save it!
                if sr.tag:
                    saveTaggedSubImage(output_folder, image_info, sr, sub_image_diff)
                else:
                    saveUntaggedSubImage(output_folder, image_info, sr, sub_image_diff)

            # Update the previous image for the next image subtraction
            previous_image = current_image

if __name__ == "__main__":
    main()
