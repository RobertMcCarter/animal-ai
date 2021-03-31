r"""
    Processes the Excel file in:
        D:\data\NRSI\1033H
"""
import pandas as pd
import numpy as np
import os

from typing import List

# First - load all the folders
excelFileToValidate = r"D:\data\NRSI\1033H\NRSI_1033H_Camera Data_2019_03_14_All Data.xlsx"

# Load the Excel file with the file paths to validate
df = pd.read_excel(excelFileToValidate, "Wildlife Camera Data_QAQC")
df = df.replace(np.nan, '', regex=True)

count = 0
taggedImagePaths: List[str] = []
for i, row in df.iterrows():
    count += 1
    # Guess the folder from the Excel file
    taggedImagePath:str = str(row["Picture File"]).strip()
    if os.path.isfile(taggedImagePath):
        print(taggedImagePath)
        taggedImagePaths.append(taggedImagePath)
    # else:
    #     print(f'Failed to find tagged image from row: {i} - "{taggedImagePath}"')

numTaggedImages = len(taggedImagePaths)
numMissingImages = count- numTaggedImages
print(f"Found a total of {numTaggedImages} tagged images - out of {count} (missing {numMissingImages})")
