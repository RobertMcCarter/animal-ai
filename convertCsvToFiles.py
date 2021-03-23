import pandas as pd
import numpy as np
import os

from typing import List, Dict


# First - load all the folders
baseDir = r"D:\data\NRSI\2263B_Turtle Nest Mound"

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

def buildMapOfSubDirs(topLevelDirs: List[str]) -> Dict[str,str]:
    """ Scan through all the of the given "top level" directories, and find all of their
        immediate sub-directories.
        Returns a dictionary where each key is the name of the sub-directory,
        and each value is the full file system path to that sub-directory.
    """
    mapOfDirs: Dict[str,str] = {}
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

print(mapOfSubDirs)


# jenniferCsvFile = os.path.join(baseDir, "files.csv")
# df = pd.read_csv(jenniferCsvFile, index_col=0)

# jenniferExcelFile = os.path.join(baseDir, "files.xlsx")
# df = pd.read_excel(jenniferExcelFile)

# print( df.dtypes )

# for i, row in df.iterrows():
#     print(i, ".  ", row.File, " -- ", row.RelativePath, " -- ", row.Folder)
