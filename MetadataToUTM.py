from importlib.resources import path
import os.path
from pathlib import Path
from GPSPhoto import gpsphoto

def getDirectory():
    print("METADATA TO UTM")
    print("===============")
    workingDir = Path(input("Enter the full file path of the folder where your images are stored:"))
    if workingDir.is_dir() == True:
        print(workingDir)
        return workingDir
    else:
        print("This is not a valid directory! Please try again.")
        return(getDirectory())

# def pullMetadata(workingDir):
#     for file in os.listdir(workingDir):
#         if Path(file).suffix == ".jpg" or Path(file).suffix == ".jpeg":
#             #print(os.path.abspath(file))
#             image = Image.open(os.path.join(workingDir, file))
#             exifData = image.getexif()
#             gpsInfo = {}
#             for tag in exifData.keys():
#                 decode = GPSTAGS.get(tag)
#                 print(decode)
                
#         else:
#             print(file + " is not a valid image type. Please make sure all images are in .jpg or .jpeg format")

def pullMetadata(workingDir):
    gpsCoordinates = {}
    for file in os.listdir(workingDir):
         if Path(file).suffix == ".jpg" or Path(file).suffix == ".jpeg":
             data = gpsphoto.getGPSData(os.path.join(workingDir, file))
             gpsCoordinates[file] = {data["Latitude"], data["Longitude"]}
    return gpsCoordinates        
pullMetadata(getDirectory())        
        
