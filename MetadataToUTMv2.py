import tkinter
from tkinter import filedialog
from pyproj import Transformer
from natsort import os_sorted
import tablib
from difflib import SequenceMatcher
from GPSPhoto import gpsphoto
import os
import simplekml

def mainMenu():
    print("METADATA TO UTM CONVERTER".center(80))
    print("===============\n".center(80))

    print ("[C] - Coordinate Conversion")
    print ("[M] - Metadata Extraction")
    print ("\n[X] - Exit Program")

    userInput = input("\nSelection: ")

    if userInput == "C" or userInput == "c":
        coordinateConversionMenu()
    elif userInput == "M" or userInput == "m":
        metadataMainMenu()
    elif userInput == "X" or userInput == "x":
        exitProgram()
    else:
        print ("\nPlease select a valid option!")
        mainMenu()
    
    exitProgram()

def metadataMainMenu():
    print ("[L] - Output Metadata to Latitude/Longitude format.")
    print ("[U] - Output Metdata to UTM zone 16N format.")
    print ("[S] - Output Metadata to State Plane - NAD83 West Georgia (US Survey ft.)")
    print ("[C] - Output Metadata to custom EPSG format.")
    print ("[P] - Output Metadata to Google Earth Path. (.kml)")
    print ("[G] - Output Metadata to Google Earth Points (.kml)")
    print ("\n[X] - Exit Program")

    userInput = input("\nSelection: ")

    if userInput == "X" or userInput == "x":
            exitProgram()
    elif userInput == "":
        print("This is not a valid input. Please try again")
        mainMenu()
    
    if userInput == "N" or userInput == "n":
        folder = getFile()
        importedData = importData(folder)
    else:
        folder = getFolder()
        importedData = importMetadata(folder)

    kml = False

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
    elif userInput == "P" or userInput == "p":
        convertedCoordinates = importedData
        writtenData = writeLineString(convertedCoordinates)
        kml = True
    elif userInput == "G" or userInput == "g":
        convertedCoordinates = importedData
        writtenData = writePoints(convertedCoordinates)
        kml = True

    exportData(folder, writtenData, kml)

def coordinateConversionMenu():
    print("[L] - State Plane to Latitude/Longitude Conversion")
    print("[S] - Latitude/Longitude to State Plane Conversion")
    print("[B] - State Plane to State Plane Conversion")
    print("[X] - Exit")

    userInput = input("\nSelection: ")

    if userInput == "X" or userInput == "x":
            exitProgram()
    elif userInput == "":
        print("This is not a valid input. Please try again")
        mainMenu()

    file = getFile()
    data = importData(file)
    if userInput == "L" or userInput == "l":
        print("This conversion format will accept any EPSG code as a source.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (US Survey ft.)")
        continueInput = input("Press `Enter` to continue...")
        EPSGZone = getEPSG(True)
        convertedCoordinates = convertCoordinates(data, EPSGZone, 4326)
        writtenData = writeData(convertedCoordinates, False)
    elif userInput == "S" or userInput == "s":
        print("This conversion format will accept any EPSG code as a target.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (US Survey ft.)")
        continueInput = input("Press `Enter` to continue...")
        EPSGZone = getEPSG()
        convertedCoordinates = convertCoordinates(data, 4326, EPSGZone)
        writtenData = writeData(convertedCoordinates, True)
    elif userInput == "B" or userInput == "b":
        print("This conversion format will accept any EPSG code as a source and target.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (US Survey ft.)")
        continueInput = input("Press `Enter` to continue...")
        EPSGFrom = getEPSG(True)
        EPSGTo = getEPSG()
        convertedCoordinates = convertCoordinates(data, EPSGFrom, EPSGTo)
        writtenData = writeData(convertedCoordinates, True)
    exportData(os.path.dirname(file), writtenData)

def getEPSG(gettingFrom = False):
    if gettingFrom:
        print("Please input the EPSG Zone that the coordinates are in.")
    else:
        print("Please input the EPSG Zone that you are converting to.")

    try:
        EPSGZone = int(input("EPSG Zone: "))
    except:
        print ("Please enter only digits for the EPSG Zone.")
        getEPSG(gettingFrom)
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

def getFile(): #responsible for displaying the UI and collecting desired selections
    while True:
        try:
            window = tkinter.Tk()
            window.wm_attributes("-topmost", 1)
            window.withdraw()
            workingFile = filedialog.askopenfilename(parent = window, filetypes = [("CSV Files", "*.csv")], initialdir = "/", title = "Select the directory which contains your coordinates.") #Tkinter allows for the creation of pop-up file directories
        except:
            workingFile = input("Enter the directory which contains your coordinates.")
        if os.path.exists(workingFile): #pathlib is incompatible with pyinstaller, so I'm using os.path
            return workingFile
        elif workingFile == "":
            exitProgram()
        else:
            print("This is not a valid .csv file! Please try again.")
            getFile()

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

def getHeader(data, toFind):
    headers = data.headers

    for header in headers:
        if SequenceMatcher(None, toFind, header.lower()).ratio() > 0.75:
            return str(header)
    
    raise ValueError(f'{toFind} not found')
    exitProgram()

def normalizeData(importedData):
    names = [] 
    x = []
    y = []
    altitudes = []
    
    try:
        x = importedData[getHeader(importedData, "easting")]
        y = importedData[getHeader(importedData, "northing")]
    except:
        x = importedData[getHeader(importedData, "latitude")]
        y = importedData[getHeader(importedData, "longitude")]
    
    try:
        altitudes = importedData[getHeader(importedData, "altitude")]
    except:
        for point in x:
            altitudes.append(0)
    finally:
        i = 0
        for point in x:
            names.append(i)
            i += 1

    normalizedData = [names, x, y, altitudes]
    return normalizedData

def importData(workingFile):
    try:
        with open(workingFile, 'r') as file:
            importedData = tablib.Dataset().load(file)
            normalizedData = normalizeData(importedData)
            return normalizedData
    except:
        print("There was an error importing the data.\n Please ensure the file exists where specified and is in the correct format.")
        exitProgram()

def convertCoordinates(importedData, EPSGFrom, EPSGTo):
    names = []
    convertedX = []
    convertedY = []
    altitudes = []
    
    transformer = Transformer.from_crs(f'EPSG:{EPSGFrom}', f'EPSG:{EPSGTo}', always_xy=True)

    for name, y, x, altitude in zip(*importedData):
        names.append(name)
        convertedCoordinate = transformer.transform(x, y)
        convertedX.append(convertedCoordinate[0])
        convertedY.append(convertedCoordinate[1])
        altitudes.append(altitude)

    convertedCoordinates = [names, convertedX, convertedY, altitudes]
    return convertedCoordinates

def writeData(convertedCoordinates, UTM):
    data = tablib.Dataset()
    data.append_col(convertedCoordinates[0], header = "NAME") #apparently with Tablib if you just append a column to an empty dataset, it will not generate the headers field properly
    data.headers = ["NAME", ]                                 #therefore, we add the headers column after appending for some reason. It works.

    if UTM:
        data.append_col(convertedCoordinates[2], header="NORTHING")
        data.append_col(convertedCoordinates[1], header="EASTING")
    else:
        data.append_col(convertedCoordinates[1], header="LATITUDE")
        data.append_col(convertedCoordinates[2], header = "LONGITUDE")
    
    data.append_col(convertedCoordinates[3], header="ALTITUDE")
    return data

def writeLineString(convertedCoordinates):
    kml = simplekml.Kml()
    lineString = kml.newlinestring(name = "Output")
    coords = []
    for pointName, latitude, longitude, altitude in zip(*convertedCoordinates):
        coords.append((longitude, latitude, altitude))
    lineString.coords = coords
    return kml

def writePoints(convertedCoordinates):
    kml = simplekml.Kml()
    for pointName, latitude, longitude, altitude in zip(*convertedCoordinates):
        point = kml.newpoint(name=pointName)
        point.coords = [(longitude, latitude, altitude)]
    return kml

def exportData(folder, data, kml = False):
    extension = ".kml" if kml else ".csv"
    outputPath = os.path.join(os.path.realpath(folder), f'output{extension}')
    if kml:
        data.save(outputPath)
    else:
        with open(outputPath, 'w', newline='') as outputFile:
            outputFile.write(data.csv)

def exitProgram():
    exitInput = input("If you would like to convert more images, please enter `yes`.")
    mainMenu() if exitInput == "yes" or exitInput == "Yes" else ""
    while True:
        exitInput = input("Press `Enter` to exit...")
        quit()

mainMenu()