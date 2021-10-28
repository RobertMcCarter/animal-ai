from typing import List
from dataclasses import dataclass

@dataclass(frozen=True)
class Region:
    """ The basic Region (rectangle) in an image
        Top left is (0,0) and x increases to the right while
        y increases down the image.
    """
    x: int
    y: int
    w: int
    h: int

    @property
    def x1(self) -> int:
        return self.x

    @property
    def y1(self) -> int:
        return self.y

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h


def intersects(a: Region, b: Region) -> bool:
    return not ( (a.x2 < b.x1 or a.x1 > b.x2) or (a.y1 > b.y2 or a.y2 < b.y1) )


@dataclass(frozen=True)
class ImageInfo:
    """ Information about a particular image in our data set
    """
    tagged: bool
    filePath: str
    regions: List[Region]


""" Simple type aliases for a list of images and a list of groups
"""
Images = List[ImageInfo]
ImageGroups = List[Images]
