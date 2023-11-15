from importlib.resources import path
import os
from natsort import os_sorted
from GPSPhoto import gpsphoto
import math
from collections import defaultdict
import csv

def getDirectory():
    selections = []
    
    print("METADATA TO UTM")
    print("===============")
    
    while True:
        workingDir = input("Enter the full file path of the folder where your images are stored:\n")
        if os.path.exists(workingDir):
            selections.append(workingDir)
            break
        else:
            print("This is not a valid directory! Please try again.")
    
    while True:
        coordinateSystem = input("Coordinate System: (l)atitude & longitude or (u)tm?\n").lower()
        if coordinateSystem != "l" and coordinateSystem != "u":
            print("Please enter a valid selection ('l' or 'c')")
        else:
            selections.append(coordinateSystem)
            break
                 
    return selections

def cleanMetadata(metadata):
    cleanedMetadata = defaultdict(list)
    for item in metadata:
        columns = []
        for value in metadata[str(item)]:
                columns.append(value)
        cleanedMetadata[item].append(columns)
    return cleanedMetadata
    

def pullMetadata(workingDir):
    metadata = {}
    for file in os_sorted(os.listdir(workingDir)):
         if file.endswith(".jpg") or file.endswith(".jpeg"):
             data = gpsphoto.getGPSData(os.path.join(workingDir, file))
             metadata[file] = {data["Latitude"], data["Longitude"]}
    return metadata

def convertToUTM(gpsCoordinates):
    #Values for UTM Band
    UTMBandChars = ["C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "X"]
    
    #Constants
    semiMajorAxis = 6378137
    semiMinorAxis = 6356752.31424518
    pi = math.pi
    e = math.e
    
    #Derived Constants
    eccentricity = math.sqrt((semiMajorAxis*semiMajorAxis)-(semiMinorAxis*semiMinorAxis))/semiMajorAxis
    eccentricityPrime = math.sqrt((semiMajorAxis*semiMajorAxis)-(semiMinorAxis*semiMinorAxis))/semiMinorAxis
    ePrime2 = eccentricityPrime*eccentricityPrime
    polarRadiusCurvature = (semiMajorAxis*semiMajorAxis)/semiMinorAxis
    
    UTMCoordinateSet = defaultdict(list)
    for coordinateSet in gpsCoordinates:
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
            numericBand = math.floor((latitude+80)/8)
            band = UTMBandChars[numericBand]
            bandAndZone = f'{zone}{band}'
            
            #Create entry in dictionary
            UTMCoordinateSet[coordinateSet].append(easting)
            UTMCoordinateSet[coordinateSet].append(northing)
            UTMCoordinateSet[coordinateSet].append(bandAndZone)
            #print(f'{coordinateSet}, LatitudeInRadians={latitudeInRadians}, LongitudeInRadians={longitudeInRadians}, A={A}, Xi={Xi}, Eta={Eta}, Ni={Ni}, Zeta={Zeta}, A1={A1}, A2={A2}, J2={J2}, J4={J4}, J6={J6}, Alpha={Alpha}, Beta={Beta}, Gamma={Gamma}, B={B}, {easting}, {northing}, {bandAndZone}')
    return UTMCoordinateSet

def csvOutput(dataToOutput, mode, fileLocation):
    fileName = os.path.join(fileLocation, "out.csv")
    with open(fileName, 'w', newline='') as csvfile:
        outputWriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        if mode == "u":
            outputWriter.writerow(['Filename'] + ['ID'] + ['UTMEasting'] + ['UTMNorthing'] + ['UTM Band and Zone'])
            i = 0
            for entry in dataToOutput:
                rowData = []
                rowData.append(entry)
                rowData.append(i)
                i += 1
                for value in dataToOutput[str(entry)]:
                    rowData.append(value[0])
                    rowData.append(value[1])
                    rowData.append(value[2])
                outputWriter.writerow([rowData[0]] + [rowData[1]] + [rowData[2]] + [rowData[3]] + [rowData[4]])
        if mode == "l":
            outputWriter.writerow(['Filename'] + ['Latitude'] + ['Longitude'])
            for entry in dataToOutput:
                rowData = []
                rowData.append(entry)
                for value in dataToOutput[str(entry)]:
                    rowData.append(value[0])
                    rowData.append(value[1])
                outputWriter.writerow([rowData[0]] + [rowData[1]] + [rowData[2]])

selections = getDirectory()
metadata = pullMetadata(selections[0])
cleanedMetadata = cleanMetadata(metadata)
UTMData = cleanMetadata(convertToUTM(cleanedMetadata))

if selections[1] == "u":
    csvOutput(UTMData, "u", selections[0])
else:
    csvOutput(cleanedMetadata, "l", selections[0])


