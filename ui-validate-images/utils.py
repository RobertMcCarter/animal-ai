import csv
import json
from typing import List, Union

def readAnimalsCsvFile( path:str ) -> List[List[Union[bool,str]]]:
    """ Read in the animals.csv file
    """
    rows: List[List[str]] = []
    with open(path, 'r') as csvfile:
        # Create a csv reader object
        csvReader = csv.reader(csvfile)

        # Extracting field names through first row
        next(csvReader)

        # Extracting each data row one by one
        row: List[Union[bool, str]]
        for row in csvReader:
            col1 = True if row[0] in ("True", "TRUE") else False
            col2 = row[1].strip()
            rows.append( [col1, col2] )
    return rows


def writeAnimalsCsvFile( path:str, data:List[List[Union[bool,str]]] ) -> None:
    """ Write out to the given file path name the new animals data.
    """
    with open(path, 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            csvWriter.writerow(row)


def saveCsvAsJson( data: List[List[Union[bool,str]]], outputPath:str ):
    # First, read in the given path as a .csv file
    jsonData = {
        "maxViewed": 0,
        "images": [ { "tagged": row[0], "filePath": row[1] } for row in data ]
    }

    # Write the output file
    with open(outputPath, "w") as json_file:
        json.dump(jsonData, json_file, indent=2)


if __name__ == "__main__":
    csvData = readAnimalsCsvFile(r"./animals.final.csv")
    saveCsvAsJson(csvData, r"./animals.json")
