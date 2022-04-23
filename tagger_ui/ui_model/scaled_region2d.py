"""
The business model core of the application.
"""
from dataclasses import dataclass
from typing import Union

import src.model as model
from src.model import Region2d


@dataclass()
class ScaledRegion2d:
    """Represents two related regions:
    The first - image region - represents the selection in the original image size.
    The second - screen region - represents the same rectangluar selection on the image
    but scaled to the size of the image on the screen.

    Also, rather than use a View Model (which just made things more complex)
    this class also stores the Tinker canvas rectangle ID.
    """

    screenRegion: Union[Region2d, None] = None
    imageRegion: Union[Region2d, None] = None

    # The Tinker canvas rectangle ID
    canvasRectId: int = 0

    def updateScreenFromImage(self, scaleFactor: float) -> None:
        """Update the screen region from the image region, using the given scaling factor
        (which defines how to go from the original image size to the screen image size)
        """
        if self.imageRegion is None:
            return
        self.screenRegion = model.scale(self.imageRegion, scaleFactor)

    def updateImageFromScreen(self, scaleFactor: float) -> None:
        """Update the image region from the screen region, using the given scaling factor
        (which defines how to go from the original image size to the screen image size)
        """
        if self.screenRegion is None:
            return
        self.imageRegion = model.scale(self.screenRegion, 1 / scaleFactor)
