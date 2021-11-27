import os
import re
import csv
import pathlib


def readAnimalsCsvFile(path: str) -> list[list[str]]:
    """Read in the animals.csv file"""
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


def writeAnimalsCsvFile(path: str, data: list[list[str]]) -> None:
    """Write out to the given file path name the new animals data."""
    with open(path, "w", newline="") as csvfile:
        csvWriter = csv.writer(csvfile, quotechar="|", quoting=csv.QUOTE_MINIMAL)
        for row in data:
            csvWriter.writerow(row)


def createSurroundingFiles(imagePath: str, distance: int) -> list[str]:
    r"""Given a file path whose file name ends in a number (ignoring the file extension)
    this function will return a list of additional files names that come
    distance before and distance after the given file name.
    For example, given `c:\dev\foo\bar\testing1234.png` and `3`, you'll get back:
    ```
       ['c:\dev\foo\bar\testing1231.png',
        'c:\dev\foo\bar\testing1232.png',
        'c:\dev\foo\bar\testing1233.png',
        # You won't get back the original file name
        'c:\dev\foo\bar\testing1235.png',
        'c:\dev\foo\bar\testing1236.png']
        'c:\dev\foo\bar\testing1237.png']
    ```
    """
    # filename is the full path and file name
    # extension has the dot and file extension
    path = pathlib.PurePath(imagePath)
    stem = path.stem

    numbers = re.findall(r"\d+", stem)  #
    fileIndexStr = numbers[0]  # File index # as a string
    baseStem = stem[
        : len(stem) - len(fileIndexStr)
    ]  # File name without image file index #
    fileIndex = int(fileIndexStr)  # File index as a number
    numberFormat = "0" + str(
        len(fileIndexStr)
    )  # We want new numbers in the same format

    result: list[str] = []

    for i in range(fileIndex - distance, fileIndex + distance + 1):
        if i == fileIndex:
            continue
        indexStr = format(i, numberFormat)
        newName = baseStem + indexStr + path.suffix
        newPath: pathlib.Path = path.with_name(newName)
        result.append(str(newPath))

    return result


def main():
    inputFilename = "./animals.csv"
    outputFilename = "./animals.out.csv"
    animalRecords = readAnimalsCsvFile(inputFilename)
    animalFileDict = {path: tag for [tag, path] in animalRecords}

    # Create the collection of new file paths
    for [_, imagePath] in animalRecords:
        surroundingFiles = createSurroundingFiles(imagePath, 5)
        for extraFile in surroundingFiles:
            if not os.path.isfile(extraFile):
                continue
            if extraFile in animalFileDict:
                continue
            animalFileDict[extraFile] = "False"

    outputRecords = [[value, path] for (path, value) in animalFileDict.items()]
    outputRecords.sort(key=lambda r: r[1])  # Sort on file path
    writeAnimalsCsvFile(outputFilename, outputRecords)


main()

# print( createSurroundingFiles(r"c:\dev\test_0123.png", 3) )
