from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    """A width/height combination - used to describe the width and height of an image
    or pair of images
    """

    width: int
    height: int


@dataclass(frozen=True)
class Region:
    """The basic Region (rectangle) in an image
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


@dataclass(frozen=True)
class TaggedRegion(Region):
    """Represents a tagged region - either `True` or `False` there is an animal in the region"""

    tag: bool


def intersects(a: Region, b: Region) -> bool:
    """Determines if the two image regions intersect at all

    Args:
        a (Region): The first region to test with
        b (Region): The second region to test with

    Returns:
        bool: `True` if the two regions intersect at all, `False` if they do not
    """
    return not ((a.x2 < b.x1 or a.x1 > b.x2) or (a.y1 > b.y2 or a.y2 < b.y1))


def intersectsAny(a: Region, testRegions: List[Region]) -> bool:
    """Determines if the `a` region intersects any region in the list of `testRegions`.

    Args:
        a (Region): The first region to test with
        testRegions (List[Region]): The second region to test with

    Returns:
        bool: `True` if the a region intersect any of the regions in `testRegions`,
              `False` if they do not
    """
    return any(intersects(a, b) for b in testRegions)


@dataclass(frozen=True)
class ImageInfo:
    """Information about a particular image in our data set"""

    tagged: bool
    filePath: str
    regions: List[Region]


""" Simple type aliases for a list of images and a list of groups
"""
Images = List[ImageInfo]
ImageGroups = List[Images]
