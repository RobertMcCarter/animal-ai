import cv2 as cv
print(f"OpenCV version: {cv.__version__}")

import model
import sub_image_extraction


# The image dimensions that we'll produce for training an AI
IMAGE_WIDTH  = 128
IMAGE_HEIGHT = 128
BLOCK_SIZE = model.Size(IMAGE_WIDTH, IMAGE_HEIGHT)




