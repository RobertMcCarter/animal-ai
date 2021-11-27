"""
The business model core of the application.
"""
from typing import List, Union

from PIL import Image

from .annotated_image import AnnotatedImage
from .scaled_region2d import ScaledRegion2d
from .timer import Timer

from src.model import Size2d, Region2d


def clearImagesOutsideRange(
    annotatedImages: List[AnnotatedImage],
    currentIndex: int,
    keepPrevious: int = 10,
    keepNext: int = 10,
) -> None:
    """Clear out of memory any loaded images that are outside the given
    range (so that we don't continue to collect in-memory images and
    consume the user's entire RAM.
    """
    # First, figure out our "keep" images in memory range
    startIndex = max(0, currentIndex - keepPrevious)
    endIndex = min(currentIndex + keepNext, len(annotatedImages) - 1)

    # Clear out images outside our range
    for i in range(0, startIndex):
        annotatedImages[i].image = None
    for i in range(endIndex + 1, len(annotatedImages)):
        annotatedImages[i].image = None


class AnnotatedImagesManager:
    """Maps the various regions on an annotated image to the screen rectangles
    being displayed
    """

    def __init__(self, annotatedImages: List[AnnotatedImage]):
        assert annotatedImages
        self._currentIndex = 0
        self.maxViewed = 0
        self._annotatedImages = annotatedImages

    # ##############################################################################################
    # region Properties
    # ##############################################################################################

    @property
    def current(self) -> AnnotatedImage:
        """The currently selected/viewed annotated image"""
        return self._annotatedImages[self._currentIndex]

    @property
    def currentIndex(self) -> int:
        """The current index within the ordered list of images"""
        return self._currentIndex

    @property
    def images(self) -> List[AnnotatedImage]:
        """The ordered list of annotated images"""
        return self._annotatedImages

    # The current rectangle the user is actively drawing on the screen
    # (which could be different from the image coordinates due to a small screen or window size)
    activeRegion: Union[ScaledRegion2d, None] = None

    def __len__(self):
        """The number of annotated images"""
        return len(self._annotatedImages)

    @property
    def windowSize(self) -> Size2d:
        """The current size of the window where the image is displayed"""
        return self._windowSize

    @property
    def scale(self) -> float:
        """The current scale factor to go from the original image to the scaled (likely down) image"""
        return self.current.scale

    @property
    def regions(self) -> List[ScaledRegion2d]:
        """The ordered collection of region view-models of interest for this image"""
        return self.current.regions

    # The current rectangle the user is actively drawing on the screen
    # (which could be different from the image coordinates due to a small screen or window size)
    activeRegion: Union[ScaledRegion2d, None] = None

    # The maximum index within the sorted list of annotated images that the user
    # has viewed (and presumably processed)
    maxViewed: int

    # The directory of images this annotated image manager collection represents
    saveFileName: str

    # endregion

    # ##############################################################################################
    # region Methods
    # ##############################################################################################

    def isValidIndex(self, index: int) -> bool:
        """Test if the given index is valid"""
        return 0 <= index < len(self._annotatedImages)

    def addActiveRegion(self) -> None:
        """Adds a new region to the current image, and returns the scaled region 2d view model"""
        if self.activeRegion is None:
            return
        self.activeRegion.canvasRectId = (
            0  # It no longer belongs to that canvas rectangle
        )
        self.current.addRegion(self.activeRegion)

        # User has "used up" the current active region
        self.activeRegion = None

    def updateActiveScreenRegion(self, screenRegion: Region2d) -> ScaledRegion2d:
        """The view should call this when the active region is changed
        (likely the user dragging the mouse).
        Returns the active scaled region.
        """
        if self.activeRegion is None:
            self.activeRegion = ScaledRegion2d(screenRegion)
        else:
            self.activeRegion.screenRegion = screenRegion

        # Now re-scale the screen region to get the "true" image region
        self.activeRegion.updateImageFromScreen(self.scale)
        return self.activeRegion

    def onWindowResized(self, newWindowSize: Size2d) -> Union[float, None]:
        """Update our current image to have the correct scale for the new canvas size
        Scale the image according to our current canvas size
        Returns the scale factor used to shrink the image to the size of the window,
        or None if the image did not change
        """
        # Save the new window size
        self._windowSize = newWindowSize

        # Scale the current image to this size
        scale = self.current.scaleImageForSize(newWindowSize)
        if scale:
            # We need to resize our Tk wrapper image
            self.current.wrapImageForTk()

            # We changed the scaling factor, so we need to re-scale the active region too
            if self.activeRegion:
                self.activeRegion.updateScreenFromImage(scale)

    def scanForTaggedIndex(self, direction: int) -> int | None:
        """Scan through starting at the current image index for the next
        image that is tagged.
        direction is either +1 or -1 to control direction.
        """
        i = self.currentIndex
        while 0 <= i < len(self._annotatedImages):
            i += direction
            if self._annotatedImages[i].isTagged:
                return i
        return None

    def moveToImage(self, index: int):
        """Open the image with the given index
        (into our ordered collection of annotated images that we received from the model layer)
        """
        assert self.isValidIndex(index)

        # Store the index that we're looking at
        self._currentIndex = index

        # Update our max viewed index
        self.maxViewed = max(self.maxViewed, self._currentIndex)

        # Ensure the image is loaded
        if self.current.image is None:
            with Timer("loading image"):
                self.current.image = Image.open(self.current.filePath)
                self.current.image.load()

        # Scale the image so it fits while retaining the correct aspect ratio
        # Only scale if we haven't already previously scaled the image (which is slow)
        # Store it back in our domain logic layer for faster access
        self.current.scaleImageForSize(self._windowSize)

        # Resize the image for the UI layer, and wrap it for Tk
        self.current.loadImage()
        self.current.scaleImageForSize(self.windowSize)
        self.current.wrapImageForTk()

        # Clear images outside of our "keep" window so we don't keep growing our memory footprint!
        clearImagesOutsideRange(self._annotatedImages, index, 10, 10)

    # endregion

    # ##############################################################################################
    # region Private data members
    # ##############################################################################################

    # The collection of annotated images we need to process for our test set
    _annotatedImages: List[AnnotatedImage]

    # The index into the _annotatedImages array,
    # So effectively, which annotated image are we currently looking at?
    _currentIndex: int = 0

    # The size of the window that is displaying our images
    _windowSize: Size2d = Size2d(500, 500)

    # endregion
