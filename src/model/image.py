from dataclasses import dataclass

from .region2d import Region2d

@dataclass(frozen=True)
class ImageInfo:
    """Information about a particular image in our data set"""

    tagged: bool
    filePath: str
    regions: list[Region2d]


@dataclass(frozen=True)
class ImagesCollection:
    """The information stored in the `animals.json` file, including metadata"""

    maxViewed: int
    images: list[ImageInfo]
