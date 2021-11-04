r"""
    Processes the Excel file in:
        D:\data\NRSI\2263B_Turtle-Nest-Mound
"""
import pandas as pd
import numpy as np
import os

from typing import List


# First - load all the folders
baseDir = r"D:\data\NRSI\2263B_Turtle-Nest-Mound"

def getDirectories( baseDir:str ) -> List[str]:
    """ Get the list of directories in the given baseDir directory
    """
    result: List[str] = []
    filenames= os.listdir(baseDir)
    for filename in filenames:  # loop through all the files and folders
        fullPath = os.path.join(baseDir, filename)
        if os.path.isdir(fullPath):
            result.append(filename)
    return result


def buildMapOfSubDirs(topLevelDirs: List[str]) -> dict[str,str]:
    """ Scan through all the of the given "top level" directories, and find all of their
        immediate sub-directories.
        Returns a dictionary where each key is the name of the sub-directory,
        and each value is the full file system path to that sub-directory.
    """
    mapOfDirs: dict[str,str] = {}
    for dir in topLevelDirs:
        path = os.path.join(baseDir, dir)
        subDirs = getDirectories(path)
        for subDir in subDirs:
            fullPath:str = os.path.join(baseDir, dir, subDir)
            if mapOfDirs.get(subDir):
                raise Exception("Found duplicate dir + sub-dir combination:" )
            mapOfDirs[subDir] = fullPath

    return mapOfDirs


# Grab the list of folders
highLevelDirs = getDirectories(baseDir)

# Now find the list of folders within those folders
# We need to build a dictionary of them mapping each sub-folder to their full path
# (because only the sub-directory is used as the "path" in our Excel files from NRSI)
mapOfSubDirs = buildMapOfSubDirs(highLevelDirs)

# Now load the original Excel file
taggedImagesExcelFile = os.path.join(baseDir, "files.xlsx")
df = pd.read_excel(taggedImagesExcelFile)
df = df.replace(np.nan, '', regex=True)

count = 0
missingFolders = set()
taggedImagePaths: List[str] = []
for i, row in df.iterrows():
    count += 1
    # Guess the folder from the Excel file
    subDir = str(row["Folder"])
    subDirPath = mapOfSubDirs.get(subDir)
    if subDirPath is None:
        missingFolders.add(row["Folder"])
        continue

    relativePath = str(row["RelativePath"])
    if relativePath != '':
        subDirPath = os.path.join(subDirPath, relativePath)

    file = str(row["File"])
    taggedImagePath = os.path.join(subDirPath, file)
    if os.path.isfile(taggedImagePath):
        print(taggedImagePath)
        taggedImagePaths.append(taggedImagePath)
    else:
        print("Failed to find tagged image from row: ", i, " - ", taggedImagePath)


numTaggedImages = len(taggedImagePaths)
numMissingImages = count- numTaggedImages
print(f"Found a total of {numTaggedImages} tagged images - out of {count} (missing {numMissingImages})")
print(f"Failed to find {len(missingFolders)} data folders")
