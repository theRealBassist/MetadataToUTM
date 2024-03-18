import tkinter
from tkinter import filedialog
from pyproj import Transformer
from collections import defaultdict
from natsort import os_sorted
import tablib
from GPSPhoto import gpsphoto
import os

def mainMenu():
    print("METADATA TO UTM CONVERTER".center(80))
    print("===============\n".center(80))

    print ("[L] - Output Metadata to Latitude/Longitude format.")
    print ("[U] - Output Metdata to UTM zone 16N format.")
    print ("[S] - Output Metadata to State Plane - NAD83 West Georgia (US Survey ft.)")
    print ("[C] - Output Metadata to custom EPSG format.")
    print ("\n[X] - Exit Program")

    userInput = input("\nSelection: ")

    if userInput == "X" or userInput == "x":
            exitProgram()
    elif userInput == "":
        print("This is not a valid input. Please try again")
        mainMenu()
    
    folder = getFolder()
    importedData = importMetadata(folder)

    if userInput == "L" or userInput == "l":
        convertedCoordinates = importedData
        writtenData = writeData(convertedCoordinates, False)
    elif userInput == "U" or userInput == "u":
        convertedCoordinates = convertCoordinates(importedData, 4326, 26916)
        writtenData = writeData(convertedCoordinates, True)
    elif userInput == "S" or userInput == "s":
        convertedCoordinates = convertCoordinates(importedData, 4326, 2240)
        writtenData = writeData(convertedCoordinates, True)
    elif userInput == "C" or userInput == "c":
        epsg = getEPSG
        convertedCoordinates = convertCoordinates(importedData, 4326, epsg)
        writtenData = writeData(convertedCoordinates, True)

    exportData(folder, writtenData)

def getEPSG():
    print("Please input the EPSG Zone that you are converting to.")

    try:
        EPSGZone = int(input())
    except:
        print ("Please enter only digits for the EPSG Zone.")
        getEPSG()
    return EPSGZone

def getFolder(): #responsible for displaying the UI and collecting desired selections
    while True:
        try:
            window = tkinter.Tk()
            window.wm_attributes("-topmost", 1)
            window.withdraw()
            workingDir = filedialog.askdirectory(initialdir = "/", title = "Select the directory which contains your images")
        except:
            workingDir = input("Enter the directory which contains your images.")
        if os.path.exists(workingDir): #pathlib is incompatible with pyinstaller, so I'm using os.path
            return workingDir
        elif workingDir == "":
            exitProgram()
        else:
            print("This is not a valid .csv file! Please try again.")
            getFolder()

def importMetadata(workingDir): #responsible for extracting metadata from the images themselves
    filenames = [] 
    latitudes = []
    longitudes = []
    altitudes = []

    files = os_sorted(os.listdir(workingDir)) #os_sorted from natsort allows the files to sort as '1, 2, 3, 4...20, 21..., 30, 31' instead of '1, 10, 11... 2, 20, 21'
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg")): #a previous iteration of this only allowed for jpgs, but this also serves as a quick check that we are actually working with images to avoid IO errors
            try:
                data = gpsphoto.getGPSData(os.path.join(workingDir, file))#the GPSPhoto library is by far the easiest way to extract the relevant metadata for this
                #altitude = gpsinfo.getAlt(os.path.join(workingDir, item))#The altitude is pulled seperately
                filenames.append(file)
                latitudes.append(data["Latitude"])
                longitudes.append(data["Longitude"])
                altitudeInFeet = data["Altitude"]*3.28084 #GPSPhoto automatically outputs the elevation in meters, so we are converting it to feet
                altitudes.append(altitudeInFeet)
            except:
                print(f"There was an error reading metadata from: {file}")#If an image does not have the relevant metadata, it will except and stop the whole script, so this handles that situation
    importedMetadata = [filenames, latitudes, longitudes, altitudes]           
    return importedMetadata

def convertCoordinates(importedData, EPSGFrom, EPSGTo):
    names = []
    convertedX = []
    convertedY = []
    altitudes = []
    
    transformer = Transformer.from_crs(f'EPSG:{EPSGFrom}', f'EPSG:{EPSGTo}', always_xy=True)

    for name, y, x, altitude in zip(importedData[0], importedData[1], importedData[2], importedData[3]):
        names.append(name)
        convertedCoordinate = transformer.transform(x, y)
        convertedX.append(convertedCoordinate[0])
        convertedY.append(convertedCoordinate[1])
        altitudes.append(altitude)

    convertedCoordinates = [names, convertedX, convertedY, altitudes]
    return convertedCoordinates

def writeData(convertedCoordinates, UTM):
    data = tablib.Dataset()
    data.append_col(convertedCoordinates[0], header = "FILENAME")
    data.headers = ["FILENAME", ]

    if UTM:
        data.append_col(convertedCoordinates[2], header="NORTHING")
        data.append_col(convertedCoordinates[1], header="EASTING")
    else:
        data.append_col(convertedCoordinates[1], header="LATITUDE")
        data.append_col(convertedCoordinates[2], header = "LONGITUDE")
    
    data.append_col(convertedCoordinates[3], header="ALTITUDE")
    return data

def exportData(folder, data):
    outputPath = os.path.join(os.path.realpath(folder), "output.csv")
    with open(outputPath, 'w', newline='') as outputFile:
        outputFile.write(data.csv)

def exitProgram():
    while True:
        exitInput = input("Press `Enter` to exit...")
        quit()

mainMenu()