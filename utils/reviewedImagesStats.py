import csv


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
