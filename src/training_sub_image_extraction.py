import cv2 as cv

print(f"OpenCV version: {cv.__version__}")

import model
import sub_image_regions


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size(IMAGE_WIDTH, IMAGE_HEIGHT)


# Numpy uses row, col notation instead of col, row

# From: https://stackoverflow.com/questions/67353650/extract-part-of-a-image-using-opencv
# or: https://stackoverflow.com/questions/15589517/how-to-crop-an-image-in-opencv-using-python
# or: https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
# `crop_img = img[y:y+h, x:x+w]`

# Aternatively, if you have defined a crop margin, you can do
# crop_img = img[margin:-margin, margin:-margin] –
