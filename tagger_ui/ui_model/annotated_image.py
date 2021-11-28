"""
The business model core of the application.
"""
import os
from tkinter import PhotoImage
from typing import List, Union, Tuple

from PIL import Image, ImageTk  # type: ignore

from .image_utils import scaleImage, isAlreadyScaledCorrectly, calculateImageScale
from .timer import Timer

import src.model as model
from src.model import Size2d

from .scaled_region2d import ScaledRegion2d


class AnnotatedImage:
    """
    An annotated image represents the image (with an optional loaded in-memory image object),
    the original image file path, and a collection of regions of interest that an AI
    model should predict.
    It can also optionally contain a scaled down version of the origina image to help
    when displaying very large images on the screen.
    """

    def __init__(self, filePath: str):
        self._filePath = filePath
        self._regions = []
        self._currentTkImage = None

    # ##############################################################################################
    # region - properties
    # ##############################################################################################

    # The in-memory loaded image for this annotated image
    # (which may be None if not loaded)
    @property
    def image(self) -> Union[Image.Image, None]:
        """The actual image represented by this annotated image,
        if it has been loaded into memory, otherwise None
        """
        return self._image

    @image.setter
    def image(self, image: Union[Image.Image, None]):
        # Update the image, and clear the scaled image, as it is no longer correct
        self._image = image
        self._scaledImage = None
        self._scale = 0.0

    _image: Union[Image.Image, None] = None

    # The image already scaled to the current window size
    # (at the time it is set - re-check the size is correct before using)
    @property
    def scaledImage(self) -> Union[Image.Image, None]:
        """The scaled (down) version of this image"""
        return self._scaledImage

    _scaledImage: Union[Image.Image, None] = None

    @property
    def scale(self) -> float:
        """The scale factor to go from the original image to the scaled (likely down) image"""
        return self._scale

    _scale: float = 0.0

    @property
    def filePath(self) -> str:
        """The full file path for this image"""
        return self._filePath

    @property
    def fileName(self) -> str:
        """The file name for this image (without the path)"""
        return os.path.basename(self._filePath)

    @property
    def regions(self) -> List[ScaledRegion2d]:
        """The ordered collection of regions of interest for this image"""
        return self._regions

    # Indicates if this image has been tagged as having an animal in it
    isTagged: bool = False

    @property
    def tkScaledImage(self) -> PhotoImage:
        """The Tk PhotoImage scaled  to the canvas size"""
        assert self._currentTkImage
        return self._currentTkImage

    # endregion - properties

    def loadImage(self) -> None:
        """Load the underlying full-size image from disk"""
        if self.image is None:
            with Timer("Loading image: " + self.fileName):
                self.image = Image.open(self.filePath)
                self.image.load()

    def clearAllRegions(self) -> None:
        """Clear all the regions from this annotated image"""
        self.isTagged = False
        self._regions.clear()

    def addRegion(self, region: ScaledRegion2d) -> Tuple[int, ScaledRegion2d]:
        """Add a new region to this annotated image"""
        # With the image region we can now create a scaled region and add it to our collection
        indexOfNewRegion = len(self._regions)
        self._regions.append(region)
        self.isTagged = True
        return (indexOfNewRegion, region)

    def scaleImage(self, scale: float) -> Image.Image:
        """Scale the main image (if there is one loaded) to the given scale.
        Returns the scaled image if it was scaled, otherwise returns None
        """
        assert self.image  # If we don't have an image we can't resize it
        self._scaledImage = scaleImage(self.image, scale)
        self._scale = scale
        return self._scaledImage

    def scaleImageForSize(self, targetSize: Size2d) -> Union[float, None]:
        """Scale the given annotated image to the target size,
        if it has an image loaded and its scale image is not already the correct size.
        Returns the scale factor used to shrink the image to the size of the window,
        or None if the image did not change
        """
        # Check pre-conditions: if we don't have an image we can't resize it
        if self.image is None:
            return

        # If we're already scaled correctly, there's nothing we need to do
        if isAlreadyScaledCorrectly(self.scaledImage, targetSize):
            assert self.scaledImage
            return None

        # Okay, now we can scale the image
        scale = calculateImageScale(self.image, targetSize)
        self.scaleImage(scale)

        # We now need to re-scale selected regions
        for region in self._regions:
            if region is not None and region.imageRegion is not None:
                region.screenRegion = model.scale(region.imageRegion, scale)
        return scale

    def wrapImageForTk(self) -> None:
        """Wrap the underlying scaled image in a Tk PhotoImage for use by the Tk UI layer"""
        assert self.scaledImage
        self._currentTkImage = ImageTk.PhotoImage(self.scaledImage)  # type: ignore

    # The current TK version of _currentImage
    # VERY IMPORTANT - Python doesn't know that TKinter will hold on to this!
    # This means without a reference here, Python will garbage collect the TkImage, and then
    # nothing works correctly and we can't show the TkImage
    # See: https://stackoverflow.com/questions/26479728/tkinter-_canvas-image-not-displaying
    # So we need to keep a reference to the TkImage object ourselves
    _currentTkImage: Union[PhotoImage, None]

    # The selected regions on this image (is any)
    _regions: List[ScaledRegion2d]
