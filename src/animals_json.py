import json
from typing import Any

from src import model


def loadAnimalsJson(fileName: str) -> model.ImagesInfo:
    """Load the animals JSON file"""

    def imageDecoder(
        dict: dict[str, Any]
    ) -> dict[str, Any] | model.Region2d | model.ImageInfo | model.ImagesInfo:
        """Decode a JSON dictionary into either a `Region` or an `ImageInfo`"""
        if "maxViewed" in dict:
            return model.ImagesInfo(maxViewed=dict["maxViewed"], images=dict["images"])
        if "x" in dict:
            return model.Region2d(x=dict["x"], y=dict["y"], w=dict["w"], h=dict["h"])
        if "tagged" in dict:
            return model.ImageInfo(
                tagged=dict["tagged"],
                filePath=dict["filePath"],
                regions=dict["regions"],
            )
        return dict

    # Opening the JSON animals data file
    with open(fileName, "rt") as f:
        data = json.load(f, object_hook=imageDecoder)
        return data


# Quick bit of test code
if __name__ == "__main__":
    # Load the animals json file
    data: list[model.ImageInfo] = loadAnimalsJson("./animals.json")

    print(data)
