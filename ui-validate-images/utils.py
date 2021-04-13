import csv
from typing import List, Union

def readAnimalsCsvFile( path:str ) -> List[List[Union[bool,str]]]:
    """ Read in the animals.csv file
    """
    rows: List[List[str]] = []
    with open(path, 'r') as csvfile:
        # Create a csv reader object
        csvReader = csv.reader(csvfile)

        # extracting field names through first row
        next(csvReader)

        # extracting each data row one by one
        row: List[Union[bool, str]]
        for row in csvReader:
            col1 = True if row[0] == "True" else False
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
