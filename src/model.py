from typing import List
from dataclasses import dataclass

@dataclass(frozen=True)
class Region:
    """ The basic Region (rectangle) in an image
    """
    x: int
    y: int
    w: int
    h: int


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
