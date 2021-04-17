import re
import csv
from pathlib import Path
from typing import List, Union

def readTaggedAnimalsCsvFile( path:str ) -> List[List[Union[str,bool]]]:
    """ Read in the latset/greatest animals CSV file
    """
    rows: List[List[Union[str,bool]]] = []
    with open(path, 'r') as csvfile:
        # create a csv reader object
        csvReader = csv.reader(csvfile)

        # extracting field names through first row
        next(csvReader)

        # extracting each data row one by one
        row: List[Union[str,bool]]
        for row in csvReader:
            rows.append(row)
    return rows


def main():
    inputFilename = "./animals.final.csv"
    animalRecords = readTaggedAnimalsCsvFile(inputFilename)

    totalTagged = 0
    totalNotTagged = 0
    for row in animalRecords:
        tagged = row[0] == "TRUE"
        if tagged:
            totalTagged += 1
        else:
            totalNotTagged += 1

    total = totalTagged + totalNotTagged
    print(f"Total tagged images: {totalTagged} - { totalTagged / total * 100}")
    print(f"Total Not tagged   : {totalNotTagged} - { totalNotTagged / total * 100}")

main()
