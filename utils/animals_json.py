import json
import cv2 as cv
from typing import List, Dict, Any
from dataclasses import dataclass

print(f"OpenCV version: {cv.__version__}")


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


def loadAnimalsJson( fileName:str ) -> List[ImageInfo]:
    """ Load the animals JSON file
    """
    def imageDecoder(dict:Dict[str, Any]):
        """ Decode a dictionary (from JSON) into either a `Region` or an `ImageInfo`
        """
        if "x" in dict:
            return Region( x=dict["x"], y=dict["y"], w=dict["w"], h=dict["h"] )
        if "tagged" in dict:
            return ImageInfo( tagged=dict["tagged"], filePath=dict["filePath"], regions=dict["regions"] )
        return dict

    # Opening the JSON animals data file
    with open(fileName, "rt") as f:
        data = json.load(f, object_hook=imageDecoder)
        return data


# Quick bit of test code
if __name__ == "__main__":
    data = loadAnimalsJson('./animals.json')
    print(data)
