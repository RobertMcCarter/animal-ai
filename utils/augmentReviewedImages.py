import re
import csv
from pathlib import Path


def readTaggedAnimalsCsvFile(path: str) -> list[list[str]]:
    """Read in the latset/greatest animals CSV file"""
    rows: list[list[str]] = []
    with open(path, "r") as csvfile:
        # create a csv reader object
        csvReader = csv.reader(csvfile)

        # extracting field names through first row
        next(csvReader)

        # extracting each data row one by one
        row: list[str]
        for row in csvReader:
            rows.append(row)
    return rows


def getPathImageIndex(path: Path) -> int:
    """Extracts the image # from the file name"""
    stem = path.stem
    numbers = re.findall(r"\d+", stem)
    fileIndexStr = numbers[0]  # File index # as a string
    fileIndex = int(fileIndexStr)  # File index as a number
    return fileIndex


def determineIfNewGroup(previousPath: Path, currentPath: Path) -> bool:
    """Determines if this is a new image group"""
    # First - if the images are in different folders it's obviously a different group
    if previousPath.parent != currentPath.parent:
        return True

    # If the indexes are not offset by 1, then it's a different group
    previousIndex = getPathImageIndex(previousPath)
    currentIndex = getPathImageIndex(currentPath)
    return (previousIndex + 1) != currentIndex


def main():
    inputFilename = "./animals.final.csv"
    animalRecords = readTaggedAnimalsCsvFile(inputFilename)

    previousPath: Path = Path(r"c:\does_not\exist.png")
    for row in animalRecords:
        tagged = row[0] == "TRUE"
        currentPath = Path(str(row[1]).strip())

        # Determine if this image group starts with a tagged image
        # (which I really don't want for DL training purposes)
        isNewGroup = determineIfNewGroup(previousPath, currentPath)
        if isNewGroup and tagged:
            print(f"Tagged image at start of group: {currentPath}")

        # Prepare for the next loop iteration
        previousPath = currentPath


main()
