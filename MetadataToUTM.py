from importlib.resources import path
import os
from natsort import os_sorted
from GPSPhoto import gpsphoto
import tkinter
from tkinter import filedialog
import math
from collections import defaultdict
import tablib
import tablib.formats._xlsx #if you don't specifically import the ._xlsx format, the program will run fine.... on your system. 
                            # to have it run after being compiled with pyinstaller, you need to specifically import this.

def getDirectory(): #responsible for displaying the UI and collecting desired selections
    selections = [] #to simplify calls later, the selections are stored in a single array
    
    print("METADATA TO UTM")
    print("===============")
    
    while True:
        try:
            tkinter.Tk().withdraw()
            workingDir = filedialog.askdirectory(initialdir = "/", title = "Select the directory which contains your images") #Tkinter allows for the creation of pop-up file directories
        except:
            workingDir = input("Enter the full file path of the folder where your images are stored:\n")
        if os.path.exists(workingDir): #pathlib is incompatible with pyinstaller, so I'm using os.path
            selections.append(workingDir)
            break
        else:
            print("This is not a valid directory! Please try again.")
    
    while True:
        coordinateSystem = input("Coordinate System: (l)atitude & longitude, (u)tm, or (b)oth?\n").lower()
        if coordinateSystem != "l" and coordinateSystem != "u" and coordinateSystem != "b":
            print("Please enter a valid selection ('l', 'b', or 'c')")
        else:
            selections.append(coordinateSystem)
            break
    
    while True:
        exportFormat = input("Export Format: (x)lsx or (c)sv?\n")
        if exportFormat != "x" and exportFormat != "c":
            print("Please enter a valid selection ('x' or 'c')")
        else:
            selections.append(exportFormat)
            break
                 
    return selections    

def pullMetadata(workingDir): #responsible for extracting metadata from the images themselves
    metadata = defaultdict(list) #using defaultdict allows for noninstantiated data to be set into the dictionary
                                 #additionally, I am using a dictionary to ease the process of calling specific filenames later
    files = os_sorted(os.listdir(workingDir)) #os_sorted from natsort allows the files to sort as '1, 2, 3, 4...20, 21..., 30, 31' instead of '1, 10, 11... 2, 20, 21'
    for item in files:
        columns = [] #I am using an array here instead of just two independent entries for the dictionary to ease the UTM calculations later
        if item.lower().endswith((".png", ".jpg", ".jpeg")): #a previous iteration of this only allowed for jpgs, but this also serves as a quick check that we are actually working with images to avoid IO errors
            try:
                data = gpsphoto.getGPSData(os.path.join(workingDir, item))#the GPSPhoto library is by far the easiest way to extract the relevant metadata for this
                columns.append(data["Latitude"])
                columns.append(data["Longitude"])
                metadata[item].append(columns)
            except:
                print(f"There was an error reading metadata from: {item}")#If an image does not have the relevant metadata, it will except and stop the whole script, so this handles that situation
                         
    return metadata

def convertToUTM(gpsCoordinates):
    #Values for UTM Band
    UTMBandChars = ["C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "X"] #UTM uses a specific set of characters, so we reference them here
    
    #Constants
    semiMajorAxis = 6378137
    semiMinorAxis = 6356752.31424518
    pi = math.pi
    e = math.e
    
    #Derived Constants #I have literally no idea how most of this works, but it does /shrug
    eccentricity = math.sqrt((semiMajorAxis*semiMajorAxis)-(semiMinorAxis*semiMinorAxis))/semiMajorAxis
    eccentricityPrime = math.sqrt((semiMajorAxis*semiMajorAxis)-(semiMinorAxis*semiMinorAxis))/semiMinorAxis
    ePrime2 = eccentricityPrime*eccentricityPrime
    polarRadiusCurvature = (semiMajorAxis*semiMajorAxis)/semiMinorAxis
    
    UTMCoordinateSet = defaultdict(list)
    for coordinateSet in gpsCoordinates:
        columns = []
        for latLong in gpsCoordinates[str(coordinateSet)]:
            latitude = latLong[0]
            longitude = latLong[1]
            #Derived Values
            latitudeInRadians = (latitude*pi)/180
            longitudeInRadians = (longitude*pi)/180
            
            spindleCalculation = math.floor((longitude/6)+31)
            spindleMeridian = (6 * spindleCalculation)-183
            deltaLambda = longitudeInRadians-((spindleMeridian*pi)/180)
            
            A = math.cos(latitudeInRadians)*math.sin(deltaLambda)
            Xi = 0.5 * math.log((1+A)/(1-A), math.e)
            Eta = math.atan((math.tan(latitudeInRadians))/math.cos(deltaLambda))-latitudeInRadians
            Ni = (polarRadiusCurvature / math.pow(1 + ePrime2 * math.pow(math.cos(latitudeInRadians), 2), 0.5))*0.9996
            Zeta = (ePrime2/2)*math.pow(Xi, 2)*math.pow(math.cos(latitudeInRadians),2)
            A1 = math.sin(2*latitudeInRadians)
            A2 = A1*math.pow(math.cos(latitudeInRadians), 2)
            J2 = latitudeInRadians+(A1/2)
            J4 = ((3*J2)+A2)/4
            J6 = ((5*J4)+(A2*math.pow(math.cos(latitudeInRadians), 2)))/3
            Alpha = 3/4 * ePrime2
            Beta = 5/3 * math.pow(Alpha, 2)
            Gamma = 35/27 * math.pow(Alpha, 3)
            B = 0.9996 * polarRadiusCurvature * (latitudeInRadians-(Alpha*J2)+(Beta*J4)-(Gamma*J6))
            
            #Actual Coordinate Calculation
            easting = Xi * Ni * (1+(Zeta/3)) + 500000
            northing = Eta * Ni * (1+Zeta) + B
            zone = spindleCalculation
            numericBand = math.floor((latitude+80)/8) #we use this value to decide which of the band letters from above we use
            band = UTMBandChars[numericBand]
            bandAndZone = f'{zone}{band}'
            
            #Create entry in dictionary
            columns.append(easting)
            columns.append(northing)
            columns.append(bandAndZone)
        UTMCoordinateSet[coordinateSet].append(columns)
    return UTMCoordinateSet

def exportData(dataToOutput, fileLocation, conversionMode, exportMode):
    outputData = tablib.Dataset() #while there are more in-depth libraries for writing .csv files, tablib is by far the easiest way to write .xlsx files
    if conversionMode == "u": #UTM data
        UTMData = convertToUTM(dataToOutput)
        outputData.headers = ["Filename", "ID", "UTM Easting", "UTM Northing", "UTM Band and Zone"] #establishes the column headers
        i = 0 #we use this counter to generate the ID column
        for entry in UTMData:
            rowData = [] #there's probably a better way to do this, but this works pretty well.
            rowData.append(entry)
            rowData.append(i)
            i += 1
            for value in UTMData[str(entry)]:
                rowData.append(value[0])
                rowData.append(value[1])
                rowData.append(value[2])
            outputData.append([rowData[0], rowData[1], rowData[2], rowData[3], rowData[4]])
    if conversionMode == "l": #lat/long data
        outputData.headers = ["Filename", "ID", "Latitude", "Longitude"]
        i = 0
        for entry in dataToOutput:
            rowData = []
            rowData.append(entry)
            rowData.append(i)
            i += 1
            for value in dataToOutput[str(entry)]:
                rowData.append(value[0])
                rowData.append(value[1])
            outputData.append([rowData[0], rowData[1], rowData[2], rowData[3]])
    if conversionMode == "b": #both
        UTMData = convertToUTM(dataToOutput)
        outputData.headers = ["Filename", "ID", "Latitude", "Longitude", "UTM Easting", "UTM Northing", "UTM Band and Zone"]
        i = 0
        for entry in dataToOutput:
            rowData = []
            rowData.append(entry)
            rowData.append(i)
            i += 1
            for value in dataToOutput[str(entry)]:
                rowData.append(value[0])
                rowData.append(value[1])
            for value in UTMData[str(entry)]:
                rowData.append(value[0])
                rowData.append(value[1])
                rowData.append(value[2])
            outputData.append([rowData[0], rowData[1], rowData[2], rowData[3], rowData[4], rowData[5], rowData[6]])
    if exportMode == "x": #xlsx export mode
        outputFileLocation = os.path.join(fileLocation, "out.xlsx")
        with open(outputFileLocation, 'wb') as f: #we have to use 'wb' as our write mode because .xlsx is a binary format, not a text format
            f.write(outputData.export('xlsx'))
    else: #csv output mode.
        outputFileLocation = os.path.join(fileLocation, "out.csv")
        with open (outputFileLocation, 'w', newline='') as f:
            f.write(outputData.export('csv'))

selections = getDirectory()
metadata = pullMetadata(selections[0])
exportData(metadata, selections[0], selections[1], selections[2])


