import os
from typing import Union


def getTestDataFolder() -> str:
    """Figure out where our test data is located"""
    baseDir = os.path.dirname(os.path.abspath(__file__))
    # print("Base dir: ", baseDir)
    testDataDir = os.path.join(baseDir, "test-data")
    return testDataDir


def getTestDataFilePath(fileName: Union[str, None] = "cat-01.jpg") -> str:
    """Returns a single test file path"""
    testDataFolder = getTestDataFolder()

    # If a particular test file was requested, return that
    if fileName:
        return os.path.join(testDataFolder, fileName)

    # Otherwise, just grab a random file
    files = os.listdir(testDataFolder)
    return files[0]
