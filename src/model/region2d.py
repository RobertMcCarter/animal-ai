from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Region2d:
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

    @property
    def right_x(self) -> int:
        """The computed right x value - basically (x + w)"""
        return self.x2

    @property
    def bottom_y(self) -> int:
        """The computed bottom y value - basically (y + h)"""
        return self.y2


# Return a new region 2d object with _all_ values scaled
# This is very useful when scaling up/down an image for display
def scale(region: Region2d, scaleFactor: float):
    """Scale this 2d region by the given scale (in both x and y directions)
    returning a new region 2d with the new scaled values
    """
    new_x: int = int(region.x * scaleFactor)
    new_y: int = int(region.y * scaleFactor)
    new_w: int = int(region.w * scaleFactor)
    new_h: int = int(region.h * scaleFactor)
    return Region2d(new_x, new_y, new_w, new_h)


def normalize(region: Region2d) -> Region2d:
    """The user may draw a rectangle "backwards" (from right to left)
        so that the width and height are negative.
        This function does the math to flip around the region 2d
        x,y,w,h values so that the width and height are positive.

    Returns:
        [Region2d]: Returns a "normalized" region 2d with a positive width and height
    """
    # If both width and height are positive, we're already normalized
    # and we can just return ourself
    if region.w > 0 and region.h > 0:
        return region

    # Either (or both) of width or height are negative, we need to create a new
    # Region2d
    x, y, w, h = region.x, region.y, region.w, region.h
    if w < 0:
        x, w = x + w, -w
    if h < 0:
        y, h = y + h, -h
    return Region2d(x, y, w, h)


def intersects(a: Region2d, b: Region2d) -> bool:
    """Determines if the two image regions intersect at all

    Args:
        a (Region): The first region to test with
        b (Region): The second region to test with

    Returns:
        bool: `True` if the two regions intersect at all, `False` if they do not
    """
    return not ((a.x2 < b.x1 or a.x1 > b.x2) or (a.y1 > b.y2 or a.y2 < b.y1))


def intersectsAny(a: Region2d, testRegions: list[Region2d]) -> bool:
    """Determines if the `a` region intersects any region in the list of `testRegions`.

    Args:
        a (Region): The first region to test with
        testRegions (list[Region]): The second region to test with

    Returns:
        bool: `True` if the a region intersect any of the regions in `testRegions`,
              `False` if they do not
    """
    return any(intersects(a, b) for b in testRegions)


@dataclass(frozen=True)
class TaggedRegion2d(Region2d):
    """Represents a tagged region - either `True` or `False` there is an animal in the region"""

    tag: bool
