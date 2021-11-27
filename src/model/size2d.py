from dataclasses import dataclass


@dataclass(frozen=True)
class Size2d:
    """A width/height combination - used to describe the width and height of an image
    or pair of images
    """

    width: int
    height: int
