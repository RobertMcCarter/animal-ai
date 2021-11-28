import json
from typing import Any
import os

from src import model


# ##################################################################################################
# region Loading json functions (de-serialization)
# ##################################################################################################


def deSerializeRegion2d(dict: dict[str, int]) -> model.Region2d:
    """Serialize a JSON dictionary back into a Region2d."""
    assert dict
    return model.Region2d(x=dict["x"], y=dict["y"], w=dict["w"], h=dict["h"])


def deSerializeImageInfo(dict: dict[str, Any]) -> model.ImageInfo:
    """Serialize a JSON dictionary back into an image information object."""
    return model.ImageInfo(
        tagged=dict["tagged"],
        filePath=dict["filePath"],
        regions=dict["regions"],
    )


def deSerializeImagesInfo(dict: dict[str, Any]) -> model.ImagesCollection:
    """Serialize a JSON dictionary back into the top-level ImagesInfo object."""
    assert dict

    currentIndex = dict["currentIndex"] if "currentIndex" in dict else 0
    return model.ImagesCollection(
        maxViewed=dict["maxViewed"],
        currentIndex=currentIndex,
        images=dict["images"],
    )


def loadImagesCollectionFromJson(file_name: str) -> model.ImagesCollection:
    """Load the animals JSON file"""
    assert file_name
    assert os.path.isfile(file_name)

    def imageDecoder(
        dict: dict[str, Any]
    ) -> dict[str, Any] | model.Region2d | model.ImageInfo | model.ImagesCollection:
        """Decode a JSON dictionary into either a `Region2d`, an `ImageInfo` or an `ImagesInfo`"""
        if "x" in dict:
            return deSerializeRegion2d(dict)
        if "tagged" in dict:
            return deSerializeImageInfo(dict)
        if "maxViewed" in dict:
            return deSerializeImagesInfo(dict)
        return dict

    # Opening the JSON animals data file
    with open(file_name, "rt") as f:
        data = json.load(f, object_hook=imageDecoder)
        return data


# endregion


# ##################################################################################################
# region Saving function (serialization)
# ##################################################################################################


def serializeRegion2dToDict(region: model.Region2d) -> dict[str, int]:
    """Serialize a Region2d into a Dict suitable for saving to JSON."""
    assert region
    nr = model.normalize(region)
    return {
        "x": nr.x,
        "y": nr.y,
        "w": nr.w,
        "h": nr.h,
    }


def serializeImageInfoToDict(image: model.ImageInfo) -> dict[str, Any]:
    """Convert an annotated image into a dictionary suitable for JSON serialization"""
    assert image
    return {
        "tagged": image.tagged,
        "filePath": image.filePath,
        "regions": [serializeRegion2dToDict(r) for r in image.regions if r is not None],
    }


def deSerializeImageCollection(collection: model.ImagesCollection) -> dict[str, Any]:
    assert collection
    return {
        "maxViewed": collection.maxViewed,
        "currentIndex": collection.currentIndex,
        "images": [
            serializeImageInfoToDict(i) for i in collection.images if i is not None
        ],
    }


def saveImagesCollectionToJson(
    file_name: str, collection: model.ImagesCollection
) -> None:
    """Saves the given collection of annotated images to the directory file"""
    assert file_name
    assert collection

    # First, we turn our annotated images manager into a dictionary with just the data
    # we actually want to persist
    data = deSerializeImageCollection(collection)

    # Now we can save that data
    with open(file_name, "w") as file:
        json.dump(data, file, indent=2)


# endregion
