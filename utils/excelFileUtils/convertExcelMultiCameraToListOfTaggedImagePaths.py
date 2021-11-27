r"""
    Processes the Excel file in:
        D:\data\NRSI\2140_Turtle Nesting-Wildlife-Cameras-2019
"""
import pandas as pd
import numpy as np
import os

# First - load all the folders
baseFolder = r"D:\data\NRSI\2140_Turtle Nesting-Wildlife-Cameras-2019"
excelFileToValidate = os.path.join(baseFolder, r"taggedImages-summary.xlsx")

# Load the Excel file with the file paths to validate
df = pd.read_excel(excelFileToValidate, "RAM-Data")
df = df.replace(np.nan, "", regex=True)

count = 0
taggedImagePaths: list[str] = []
for i, row in df.iterrows():
    count += 1

    # Try and figure out the tagged image name
    camera = "Camera-" + str(row["Camera"])
    subFolder = str(row["Folder"])
    file = str(row["File"])

    taggedImagePath: str = os.path.join(baseFolder, camera, subFolder, file)
    if os.path.isfile(taggedImagePath):
        print(taggedImagePath)
        taggedImagePaths.append(taggedImagePath)
    # else:
    #     print(f'Failed to find tagged image from row: {i} - "{taggedImagePath}"')


numTaggedImages = len(taggedImagePaths)
numMissingImages = count - numTaggedImages
print(
    f"Found a total of {numTaggedImages} tagged images - out of {count} (missing {numMissingImages})"
)
