import json
from typing import Dict, Any

import model

def loadAnimalsJson( fileName:str ) -> model.Images:
    """ Load the animals JSON file
    """
    def imageDecoder(dict:Dict[str, Any]) -> Dict[str,Any] | model.Region | model.ImageInfo:
        """ Decode a JSON dictionary into either a `Region` or an `ImageInfo`
        """
        if "x" in dict:
            return model.Region( x=dict["x"], y=dict["y"], w=dict["w"], h=dict["h"] )
        if "tagged" in dict:
            return model.ImageInfo( tagged=dict["tagged"], filePath=dict["filePath"], regions=dict["regions"] )
        return dict

    # Opening the JSON animals data file
    with open(fileName, "rt") as f:
        data = json.load(f, object_hook=imageDecoder)
        return data


# Quick bit of test code
if __name__ == "__main__":
    data = loadAnimalsJson('./animals.json')
    print(data)
