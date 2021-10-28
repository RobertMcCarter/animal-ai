import re
from pathlib import Path
from typing import List

import model

def groupImages( images: model.Images ) -> model.ImageGroups:
    """ Aggregate images into groups of the same file name by index range
    """
    previousPath = None
    previousIndex = None
    results: List[List[model.ImageInfo]] = []
    currentGroup: List[model.ImageInfo] = []
    for image in images:
        # Grab the previous path and index #
        p = Path(image.filePath)
        path = p.parents[0]
        index = int( re.findall(r"\d+", p.stem)[0] )

        # Is this a new group?
        isNewPath = path != previousPath
        isUnExpectedIndex = previousIndex is None or index != previousIndex + 1
        # print(f"PATH: {p} - New? {isNewPath}  Index: {isUnExpectedIndex}")
        if isNewPath or isUnExpectedIndex:
            # Create a new group and add it to our collection of groups
            currentGroup = []
            results.append(currentGroup)

        previousPath = path
        previousIndex = index
        currentGroup.append(image)

    return results
