import arcpy
import math
import os
import sys
import tempfile
import datetime
from datetime import date, datetime
import time

from arcpy import env

def getDegree(DD):
    degree = int(DD)

    return degree

def getMinute(DD):
    degree = int(DD)

    if DD >= 0:
        r1 = DD - degree
        r1 = r1*60
        minutes = int(r1)

        return minutes

    elif DD < 0:
        r1 = math.fabs(DD)+degree
        r1 = r1*60
        minutes = int(r1)

        return minutes

def getSecond(DD):
    degree = int(DD)

    if DD >= 0:
        r1 = DD - degree
        r1 = r1*60
        minutes = int(r1)
        seconds = (r1-minutes)*60

        return seconds

    elif DD < 0:
        r1 = math.fabs(DD)+degree
        r1 = r1*60
        minutes = int(r1)
        seconds = (r1-minutes)*60

        return seconds

def range_azimuth(longit_sp, latit_sp, longit_ep, latit_ep):
    #Math will be done here to calculate the azimuth from the parameters provided

    latit_ep = float(latit_ep)
    longit_ep = float(longit_ep)
    deg_to_rad = math.pi/180

    delta_lat = math.fabs(latit_ep-latit_sp)
    delta_long = math.fabs(longit_ep-longit_sp)
    #Math used to calculate the distance between two points
    a = (math.sin(deg_to_rad*delta_lat/2)**2) + math.cos(deg_to_rad*latit_sp)*math.cos(deg_to_rad*latit_ep)*(math.sin(deg_to_rad*delta_long/2)**2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    distance = 6371*c

    #Math used to calculate the azimuth between two points
    p1 = math.sin(delta_long*deg_to_rad)*math.cos(latit_ep*deg_to_rad)
    p2 = math.cos(latit_sp*deg_to_rad)*math.sin(latit_ep*deg_to_rad)
    p3 = math.sin(latit_sp*deg_to_rad)*math.cos(latit_ep*deg_to_rad)*math.cos(delta_long*deg_to_rad)
    azimuth = math.atan2(p1,p2-p3)
    azimuth = azimuth *(180.0/math.pi)
    azimuth = (azimuth+360)%360

    return [distance, azimuth]

# Convert units
def convertUnits(cunit):
    rng = float(cunit.split(" ")[0])
    unt = cunit.split(" ")[1]
    if unt == "Miles":
        crange = str(rng*0.6213711922) + " " + unt
    elif unt == "Unknown":
        crange = str(rng) + " " + unt

    return crange

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PFRR Tools"
        self.alias = "PFRR Tools"

        # List of tool classes associated with this toolbox
        self.tools = [Ending_Point, Range_Distance, PFRR]

class Ending_Point(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3) Ending Point"
        self.description = "This tool calculates the final point given" + \
        "the initial point, range and bearing."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Initial Point Lon (in Decimal Degrees)",
            name="splon",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Initial Point Lat (in Decimal Degrees)",
            name="splat",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Distance (in Kilometers)",
            name="Distance",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        param3 = arcpy.Parameter(
            displayName="Azimuth (Degrees)",
            name="Azimuth",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Report",
            name="Repfile",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

##        # Fourth param
##        param3 = arcpy.Parameter(
##            displayName="Slurp"
##            name="slurp"
##            datatype="GPFeatureLayer"
##            parameterType="Derived"
##            direction="Output")

        # param2.parameterDependencies = [param0.name]
        # param2.schema.clone = True

        params = [param0, param1, param2, param3, param4]
        param0.value = ""       # pfrr lon
        param1.value = ""       # pfrr lat
        param2.value = ""       # distance
        param3.value = ""       # azimuth
        param4.value = ""       # Report Name

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        distance = float(parameters[2].valueAsText)
        azi = float(parameters[3].valueAsText)
        report = parameters[4].valueAsText
        latit_sp = float(parameters[1].valueAsText)
        longit_sp = float(parameters[0].valueAsText)

        #Calculates Angular Distance
        ang_distance = distance/6371

        #Calculate the ending point latitude
        p1 = math.sin(math.radians(latit_sp))*math.cos(ang_distance)
        p2 = math.cos(math.radians(latit_sp))*math.sin(ang_distance)*math.cos(math.radians(azi))
        lat_ep = math.degrees(math.asin(p1+p2))

        #Calculate the ending point longitude
        p3 = math.sin(math.radians(azi))*math.sin(ang_distance)*math.cos(math.radians(latit_sp))
        p4 = math.cos(ang_distance) - (math.sin(math.radians(latit_sp))*math.sin(math.radians(lat_ep)))
        long_ep = longit_sp + math.degrees(math.atan2(p3,p4))

        outshp = os.path.splitext(report)[0]+ '.shp'

        point = arcpy.Point(latit_sp,longit_sp)
        end_point = arcpy.Point(lat_ep,long_ep)

        ptGeometry = arcpy.PointGeometry(point)
        ptGeometry2 = arcpy.PointGeometry(end_point)

        degree = int(latit_sp)
        r1 = 0
        minutes = 0
        seconds = 0

        report_h = open(report,"w")
        report_h.write("SP_Lat_DD" + "\n" + latit_sp)
        # report_h.write("\nStarting Point Latitude: ")
        #report_h.write(str(getDegree(latit_sp)) + "? " + str(getMinute(latit_sp)) + " minutes " + str(getSecond(latit_sp)) + " seconds")
        report_h.write("SP_Lon_DD" + "\n" + longit_sp)
        # report_h.write("\nStarting Point Longitude: ")
        report_h.write(str(getDegree(longit_sp)) + "? " + str(getMinute(longit_sp)) + " minutes " + str(getSecond(longit_sp)) + " seconds")
        report_h.write("\nYour Range in Kilometers: " + str(distance))
        report_h.write("\nYour Range in Nautical Miles: " + str(distance*0.539957))
        report_h.write("\nYour Range in Miles: " + str(distance*0.621371))
        report_h.write("\nYour Range in Yards: " + str(distance*1093.61))
        report_h.write("\nYour Range in Feet: " + str(distance*3280.84))
        report_h.write("\nYour Range in Meters: " + str(distance*1000))
        report_h.write("\nYour Azimuth in Degrees: " + str(azi))
        report_h.write("\nEnding Point Latitude: " + str(lat_ep))
        report_h.write("\nEnding Point Latitude: ")
        report_h.write(str(getDegree(lat_ep)) + "? " + str(getMinute(lat_ep)) + " minutes " + str(getSecond(lat_ep)) + " seconds")
        report_h.write("\nEnding Point Latitude: " + str(long_ep))
        report_h.write("\nEnding Point Longitude: ")
        report_h.write(str(getDegree(long_ep)) + "? " + str(getMinute(long_ep)) + " minutes " + str(getSecond(long_ep)) + " seconds")
        report_h.close()

        return

class Range_Distance(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2) Range and Bearing"
        self.description = "This tool calculates the range and bearing between " + \
        "two points (starting and ending points)."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Zero param -- Boolean unchecked == DD, checked == DMS
        param0 = arcpy.Parameter(
            displayName="Enter as DMS",
            name="dms",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        # First parameter
        param1 = arcpy.Parameter(
            displayName="Starting Point Lon (in Decimal Degrees)",
            name="splon",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")


        # Second parameter
        param2 = arcpy.Parameter(
            displayName="Starting Point Lat (in Decimal Degrees)",
            name="splat",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Third parameter
        param3 = arcpy.Parameter(
            displayName="Ending Point Lon (in Decimal Degrees)",
            name="fplon",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Fourth parameter
        param4 = arcpy.Parameter(
            displayName="Ending Point Lat (in Decimal Degrees)",
            name="fplat",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Fifth parameter -- DMS lon start
        param5 = arcpy.Parameter(
            displayName = "Start Longitude - Degrees Minutes Seconds - (Enter West as negative degrees)",
            name = "dmsSpLon",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Sixth parameter -- DMS lat start
        param6 = arcpy.Parameter(
            displayName = "Start Latitude - Degrees Minutes Seconds - (Enter South as negative degrees)",
            name = "dmsSpLat",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Seventh parameter -- DMS lon end
        param7 = arcpy.Parameter(
            displayName = "End Longitude - Degrees Minutes Seconds - (Enter West as negative degrees)",
            name = "dmsFpLon",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Eighth parameter -- DMS lat end
        param8 = arcpy.Parameter(
            displayName = "End Latitude - Degrees Minutes Seconds - (Enter South as negative degrees)",
            name = "dmsFpLat",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Ninth param - Range
        param9 = arcpy.Parameter(
            displayName="Range (Kilometers)",
            name="km",
            datatype="GPVariant",
            parameterType="Optional",
            direction="Input")

        # Tenth param - Range Unit Converter
        param10 = arcpy.Parameter(
            displayName="Convert Range To:",
            name="units",
            datatype="GPLinearUnit",
            parameterType="Optional",
            direction="Input")

        # Eleventh param - Azimuth
        param11 = arcpy.Parameter(
            displayName="Bearing (Degrees Azimuth)",
            name="az",
            datatype="GPVariant",
            parameterType="Optional",
            direction="Input")

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]

        # Default disabled params
        param5.enabled = 0
        param6.enabled = 0
        param7.enabled = 0
        param8.enabled = 0
        param10.enabled = 0

        # Default param values
        param10.value = "0 Unknown"

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if not parameters[0].altered:   # DMS unchecked
            if parameters[1].altered:   # Start DD Lon
                ddx1 = parameters[1].valueAsText
                dx1 = ddx1.split(".")[0]
                # parameters[4].value = dx
                mx1 = (float(ddx1) - float(dx1))*-60
                # parameters[5].value = int(mx)
                sx1 = round((mx1 - int(str(mx1).split(".")[0]))*60, 6)
                # parameters[6].value = sx
                if parameters[1].value < 0:  # Start DMS Lon and Lat
                    # fancy version -- parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                    parameters[5].value = str(int(dx1)) + " " + str(int(mx1)) + " " + str(sx1)

            if parameters[2].altered:   # Start DD Lat
                ddy1 = parameters[2].valueAsText
                dy1 = ddy1.split(".")[0]
                # parameters[7].value = dy
                my1 = (float(ddy1) - float(dy1))*60
                # parameters[8].value = int(my)
                sy1 = round((my1 - int(str(my1).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[6].value = str(int(dy1)) + " " + str(int(my1)) + " " + str(sy1)

            if parameters[3].altered:   # End DD Lon
                ddx2 = parameters[3].valueAsText
                dx2 = ddx2.split(".")[0]
                # parameters[4].value = dx
                mx2 = (float(ddx2) - float(dx2))*-60
                # parameters[5].value = int(mx)
                sx2 = round((mx2 - int(str(mx2).split(".")[0]))*60, 6)
                # parameters[6].value = sx
                if parameters[3].value < 0:  # End DMS Lon and Lat
                    # fancy version -- parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                    parameters[7].value = str(int(dx2)) + " " + str(int(mx2)) + " " + str(sx2)

            if parameters[4].altered:   # End DD Lat
                ddy2 = parameters[4].valueAsText
                dy2 = ddy2.split(".")[0]
                # parameters[7].value = dy
                my2 = (float(ddy2) - float(dy2))*60
                # parameters[8].value = int(my)
                sy2 = round((my2 - int(str(my2).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[8].value = str(int(dy2)) + " " + str(int(my2)) + " " + str(sy2)

            if parameters[1].value and parameters[2].value and parameters[3].value and parameters[4].value:
                spx = float(parameters[1].valueAsText)
                spy = float(parameters[2].valueAsText)
                epx = float(parameters[3].valueAsText)
                epy = float(parameters[4].valueAsText)
                rd = range_azimuth(spx, spy, epx, epy)    # rng = range
                parameters[9].value = str(round(rd[0],1))
                parameters[10].enabled = 1
                #parameters[10].value = parameters[9].valueAsText + " Kilometers"
                if parameters[9].altered:
                    parameters[10].value = parameters[9].valueAsText + " Kilometers"
                if parameters[10].altered:
                    parameters[10].value = convertUnits(parameters[10].valueAsText)
                parameters[11].value = str(round(((rd[1]*-1)+360),1)) + u'\xb0'





        if parameters[0].altered:   # DMS checked
            if parameters[0].value:
                parameters[1].enabled = 0
                parameters[2].enabled = 0
                parameters[3].enabled = 0
                parameters[4].enabled = 0
                parameters[5].enabled = 1
                parameters[6].enabled = 1
                parameters[7].enabled = 1
                parameters[8].enabled = 1
                if parameters[5].altered:   # Start DMS Lon
                    degx1 = int(parameters[5].valueAsText.split(" ")[0])*-1
                    minx1 = float(parameters[5].valueAsText.split(" ")[1])
                    secx1 = float(parameters[5].valueAsText.split(" ")[2])
                    parameters[1].value = (degx1 + (minx1/60 + secx1/3600))*-1

                if parameters[6].altered:   # Start DMS Lat
                    degy1 = int(parameters[6].valueAsText.split(" ")[0])
                    miny1 = float(parameters[6].valueAsText.split(" ")[1])
                    secy1 = float(parameters[6].valueAsText.split(" ")[2])
                    parameters[2].value = degy1 + (miny1/60 + secy1/3600)

                if parameters[7].altered:   # End DMS Lon
                    degx2 = int(parameters[7].valueAsText.split(" ")[0])*-1
                    minx2 = float(parameters[7].valueAsText.split(" ")[1])
                    secx2 = float(parameters[7].valueAsText.split(" ")[2])
                    parameters[3].value = (degx2 + (minx2/60 + secx2/3600))*-1

                if parameters[8].altered:    # End DMS Lat
                    degy2 = int(parameters[8].valueAsText.split(" ")[0])
                    miny2 = float(parameters[8].valueAsText.split(" ")[1])
                    secy2 = float(parameters[8].valueAsText.split(" ")[2])
                    parameters[4].value = degy2 + (miny2/60 + secy2/3600)

                if parameters[1].value and parameters[2].value and parameters[3].value and parameters[4].value:
                    spx = float(parameters[1].valueAsText)
                    spy = float(parameters[2].valueAsText)
                    epx = float(parameters[3].valueAsText)
                    epy = float(parameters[4].valueAsText)
                    rd = range_azimuth(spx, spy, epx, epy)    # rd = range and direction
                    parameters[9].value = str(round(rd[0],1))
                    #parameters[10].value = str(round(rd[0],1)) + " Kilometers"
                    parameters[11].value = str(round(rd[1],1)) + u'\xb0'

            else:    # DMS checked then unchecked
                parameters[1].enabled = 1
                parameters[2].enabled = 1
                parameters[3].enabled = 1
                parameters[4].enabled = 1
                parameters[5].enabled = 0
                parameters[6].enabled = 0
                parameters[7].enabled = 0
                parameters[8].enabled = 0
            if parameters[1].altered:   # Start DD Lon
                ddx1 = parameters[1].valueAsText
                dx1 = ddx1.split(".")[0]
                # parameters[4].value = dx
                mx1 = (float(ddx1) - float(dx1))*-60
                # parameters[5].value = int(mx)
                sx1 = round((mx1 - int(str(mx1).split(".")[0]))*60, 6)
                # parameters[6].value = sx
                if parameters[1].value < 0:  # Start DMS Lon and Lat
                # fancy version -- parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                    parameters[5].value = str(int(dx1)) + " " + str(int(mx1)) + " " + str(sx1)

            if parameters[2].altered:   # Start DD Lat
                ddy1 = parameters[2].valueAsText
                dy1 = ddy1.split(".")[0]
                # parameters[7].value = dy
                my1 = (float(ddy1) - float(dy1))*60
                # parameters[8].value = int(my)
                sy1 = round((my1 - int(str(my1).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[6].value = str(int(dy1)) + " " + str(int(my1)) + " " + str(sy1)

            if parameters[3].altered:   # End DD Lon
                ddx2 = parameters[3].valueAsText
                dx2 = ddx2.split(".")[0]
                # parameters[4].value = dx
                mx2 = (float(ddx2) - float(dx2))*-60
                # parameters[5].value = int(mx)
                sx2 = round((mx2 - int(str(mx2).split(".")[0]))*60, 6)
                # parameters[6].value = sx
                if parameters[3].value < 0:  # End DMS Lon and Lat
                    # fancy version -- parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                    parameters[7].value = str(int(dx2)) + " " + str(int(mx2)) + " " + str(sx2)

            if parameters[4].altered:   # End DD Lat
                ddy2 = parameters[4].valueAsText
                dy2 = ddy2.split(".")[0]
                # parameters[7].value = dy
                my2 = (float(ddy2) - float(dy2))*60
                # parameters[8].value = int(my)
                sy2 = round((my2 - int(str(my2).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[8].value = str(int(dy2)) + " " + str(int(my2)) + " " + str(sy2)

            if parameters[1].value and parameters[2].value and parameters[3].value and parameters[4].value:
                spx = float(parameters[1].valueAsText)
                spy = float(parameters[2].valueAsText)
                epx = float(parameters[3].valueAsText)
                epy = float(parameters[4].valueAsText)
                rd = range_azimuth(spx, spy, epx, epy)    # rd = range and direction
                parameters[9].value = str(round(rd[0],1))
                #parameters[10].value = str(round(rd[0],1)) + " Kilometers"
                parameters[11].value = str(round(rd[1],1)) + u'\xb0'

##        if parameters[9].altered:
##            parameters[9].value = str(convertUnits(parameters[9].valueAsText.split(" ")[0], parameters[9].valueAsText.split(" ")[1])) + " " + parameters[9].valueAsText.split(" ")[1]
##            range = parameters[9].valueAsText
##            nrd = parameters[10]valueAsText
##            nunit = nrd.split(" ")[1]
##            nrange = convertUnits(range, nunit)
##            parameters[10].value = nrange + " " + nunit

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        return


class PFRR(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1) PFRR Pre-launch"
        self.description = "This tool plots the predicted impact point (Lon,Lat) " + \
        "then calculates a 3sigma cirlce centered on the predicted impact point, and " + \
        "intersects the circle with underlying Land Ownership to output a new " + \
        "land_ownership_within_3sigma layer in the map"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Zero Parameter -- Mission Name
        param0 = arcpy.Parameter(
            displayName="Mission Name:",
            name="mission",
            datatype="GPType",
            parameterType="Required",
            direction="Input")

        # First param -- Boolean unchecked == DD, checked == DMS
        param1 = arcpy.Parameter(
            displayName="Enter as DMS",
            name="dms",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        # Second parameter -- DD Lon
        param2 = arcpy.Parameter(
            displayName="Input Lon (in Decimal Degrees)",
            name="lon",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Third parameter -- DD Lat
        param3 = arcpy.Parameter(
            displayName="Input Lat (in Decimal Degrees)",
            name="lat",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Eleventh parameter -- DMS lon read-out
        param4 = arcpy.Parameter(
            displayName = "Degrees Minutes Seconds - Longitude (Enter West as negative degrees)",
            name = "dmsLon",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Twelvth parameter -- DMS lat read-out
        param5 = arcpy.Parameter(
            displayName = "Degrees Minutes Seconds - Latitude (Enter South as negative degrees)",
            name = "dmsLat",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        # Tenth parameter -- Radius
        param6 = arcpy.Parameter(
            displayName="Input 3sigma Cirlce Radius (in Nautical Miles)",
            name="radius",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")


        # param2.parameterDependencies = [param0.name]
        # param2.schema.clone = True
        # parameter list
        params = [param0, param1, param2, param3, param4, param5, param6]  # param4, param5, param6, param7, param8, param9,

        # default parameter values
        param0.value = "TestMission"  # + datetime.now().strftime("%Y%m%d%H%M")
        param2.value = 0  #-149.906682
        param3.value = 0  #67.264536
        param6.value = 21

        # default disabled params
        param4.enabled = 0
        param5.enabled = 0


        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""



        if not parameters[1].altered:
            if parameters[2].altered:
                ddx = parameters[2].valueAsText
                dx = ddx.split(".")[0]
                # parameters[4].value = dx
                mx = (float(ddx) - float(dx))*-60
                # parameters[5].value = int(mx)
                sx = round((mx - int(str(mx).split(".")[0]))*60, 6)
                # parameters[6].value = sx

            if parameters[3].altered:
                ddy = parameters[3].valueAsText
                dy = ddy.split(".")[0]
                # parameters[7].value = dy
                my = (float(ddy) - float(dy))*60
                # parameters[8].value = int(my)
                sy = round((my - int(str(my).split(".")[0]))*60, 6)
                # parameters[9].value = sy

            if parameters[2].value < 0:
                # fancy version -- parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                parameters[4].value = str(int(dx)) + " " + str(int(mx)) + " " + str(sx)
                parameters[5].value = str(int(dy)) + " " + str(int(my)) + " " + str(sy)

        if parameters[1].altered:
            if parameters[1].value:
                parameters[2].enabled = 0
                parameters[3].enabled = 0
                parameters[4].enabled = 1
                parameters[5].enabled = 1
                if parameters[4].altered:
                    degx = int(parameters[4].valueAsText.split(" ")[0])*-1
                    minx = float(parameters[4].valueAsText.split(" ")[1])
                    secx = float(parameters[4].valueAsText.split(" ")[2])
                    parameters[2].value = (degx + (minx/60 + secx/3600))*-1

                if parameters[5].altered:
                    degy = int(parameters[5].valueAsText.split(" ")[0])
                    miny = float(parameters[5].valueAsText.split(" ")[1])
                    secy = float(parameters[5].valueAsText.split(" ")[2])
                    parameters[3].value = degy + (miny/60 + secy/3600)

            else:
                parameters[2].enabled = 1
                parameters[3].enabled = 1
                parameters[4].enabled = 0
                parameters[5].enabled = 0
                if parameters[2].altered:
                    ddx = parameters[2].valueAsText
                    dx = ddx.split(".")[0]
                    # parameters[4].value = dx
                    mx = (float(ddx) - float(dx))*-60
                    # parameters[5].value = int(mx)
                    sx = round((mx - int(str(mx).split(".")[0]))*60, 6)
                    #parameters[6].value = sx

                if parameters[3].altered:
                    ddy = parameters[3].valueAsText
                    dy = ddy.split(".")[0]
                    # parameters[7].value = dy
                    my = (float(ddy) - float(dy))*60
                    # parameters[8].value = int(my)
                    sy = round((my - int(str(my).split(".")[0]))*60, 6)
                    # parameters[9].value = sy

                if parameters[2].value < 0:
                    # fancy version - parameters[11].value = "W " + str(int(dx)*-1) + u'\xb0' + " " + str(int(mx)) + "' " + str(sx) + '", ' + "N " + str(dy) + u'\xb0' + " " + str(int(my)) + "' " + str(sy) + '"'
                    parameters[4].value = str(int(dx)) + " " + str(int(mx)) + " " + str(sx)
                    parameters[5].value = str(int(dy)) + " " + str(int(my)) + " " + str(sy)



        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # local variables and env
        arcpy.CreateFileGDB_management("E:/gina/poker/gdb", parameters[0].valueAsText)
        arcpy.env.workspace = "E:/gina/poker/gdb/" + parameters[0].valueAsText + ".gdb"
        arcpy.env.overwriteOutput = True
        adnr_lo_shp = "E:/gina/poker/shp/wip/land_ownership_data/adnr_gls_dls_merge_20170823_v1.shp"
        pfrr_popn_places = "E:/gina/poker/shp/wip/popn_places_data/pokerflat_popn_places_gcs_wgs84_to_akalbers_2.shp"
        afs_known_sites = "E:/gina/poker/shp/afs_data/afs_known_sites_20180629_3338.shp"
        pipTable = "E:/gina/poker/dbf/predicted_impact_xy.dbf"
        pip_point_shp = "E:/gina/poker/pip/pip_point.shp"
        pip_point_3338 = "E:/gina/poker/pip/pip_point_3338.shp"
        pip_buffer_shp = "E:/gina/poker/pip/pip_buffer.shp"
        pip_range_rings_shp = "E:/gina/poker/pip/pip_range_rings.shp"
        pip_lo_in_buffer_shp = "E:/gina/poker/pip/pip_lo_in_buffer.shp"
        pip_lo_in_buf_sum_dbf = "E:/gina/poker/pip/pip_lo_in_buf_sum.dbf"
        pip_lo_in_buf_sum_csv = "E:/gina/poker/pip/pip_lo_in_buf_sum.csv"
        pip_popn_places_in_buffer_shp = "E:/gina/poker/pip/pip_popn_places_in_buffer.shp"
        pip_known_sites_in_buffer_shp = "E:/gina/poker/pip/pip_known_sites_in_buffer.shp"
        x = parameters[2].valueAsText
        y = parameters[3].valueAsText
        r = parameters[6].valueAsText + " NauticalMiles"
        rr1 = (float(parameters[6].valueAsText))/3
        rr2 = (rr1*2)
        rrs = str(rr1) + ";" + str(rr2) + ";" + r.split(" ")[0]
        pipLayer = "pipLayer1"
        srs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")
        intersect_fc1 = [adnr_lo_shp, pip_buffer_shp]
        intersect_fc2 = [pfrr_popn_places, pip_buffer_shp]
        intersect_fc3 = [afs_known_sites, pip_buffer_shp]
        mxd = arcpy.mapping.MapDocument("current")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
        sourceLoSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/lo2.lyr")
        sourcePipSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/pip2.lyr")
        sourceRrsSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/rrs.lyr")
        sourcePopSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/pop.lyr")
        sourceAfsSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/afs2.lyr")


        # Process: Calculate Lon Field
        arcpy.CalculateField_management(pipTable, "Lon", x, "PYTHON", "")

        # Process: Calculate Lat Field
        arcpy.CalculateField_management(pipTable, "Lat", y, "PYTHON", "")

        # Process: Make XY Event Layer
        arcpy.MakeXYEventLayer_management(pipTable, "Lon", "Lat", pipLayer, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "")

        # Process: Copy Features
        arcpy.CopyFeatures_management(pipLayer, pip_point_shp, "", "0", "0", "0")

        # Process: Project pip point
        arcpy.Project_management(pip_point_shp, pip_point_3338, srs)

        # Process: Buffer pip point
        arcpy.Buffer_analysis(pip_point_3338, pip_buffer_shp, r, "FULL", "ROUND", "NONE", "", "PLANAR")

        # Process: Multiple Ring Buffer
        arcpy.MultipleRingBuffer_analysis(pip_point_3338, pip_range_rings_shp, rrs, "NauticalMiles", "", "NONE", "FULL")

        # Process: Intersect pip buffer with land ownership
        arcpy.Intersect_analysis(intersect_fc1, pip_lo_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Intersect pip buffer with popn places
        arcpy.Intersect_analysis(intersect_fc2, pip_popn_places_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Intersect pip buffer with afs known sites
        arcpy.Intersect_analysis(intersect_fc3, pip_known_sites_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Make feature layers and add to the map
        ## pip feature class list
        fclist = arcpy.ListFeatureClasses()

        ## pip layer
        arcpy.MakeFeatureLayer_management(pip_point_3338, "Predicted Impact Point")

        ## land ownership layer
        arcpy.MakeFeatureLayer_management(pip_lo_in_buffer_shp, "Land Ownership within 3sigma of Predicted Impact Point")

        ## Range Rings
        arcpy.MakeFeatureLayer_management(pip_range_rings_shp, "Range Rings")

        ## populated places layer
        popn_places_records = int(arcpy.GetCount_management(pip_popn_places_in_buffer_shp).getOutput(0))
        if popn_places_records > 0:
            arcpy.MakeFeatureLayer_management(pip_popn_places_in_buffer_shp, "Populated Places within 3sigma of Predicted Impact Point")
            addPipPopnPlacesLayer = arcpy.mapping.Layer("Populated Places within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipPopnPlacesLayer)

        ## known sites layer
        known_sites_records = int(arcpy.GetCount_management(pip_known_sites_in_buffer_shp).getOutput(0))
        if known_sites_records > 0:
            arcpy.MakeFeatureLayer_management(pip_known_sites_in_buffer_shp, "AFS Known Sites within 3sigma of Predicted Impact Point")
            addPipKnownSitesLayer = arcpy.mapping.Layer("AFS Known Sites within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipKnownSitesLayer)

        addPipPointLayer = arcpy.mapping.Layer("Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, addPipPointLayer)

        add3sigmaLoLayer = arcpy.mapping.Layer("Land Ownership within 3sigma of Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, add3sigmaLoLayer)

        addRangeRings = arcpy.mapping.Layer("Range Rings")
        arcpy.mapping.AddLayer(dataframe, addRangeRings)


        # Add and calc Acres field for intersected Land Ownership
        arcpy.AddField_management(pip_lo_in_buffer_shp, "Acres", "DOUBLE")
        arcpy.CalculateField_management(pip_lo_in_buffer_shp, "Acres", "!shape.area@acres!", "PYTHON_9.3", "")

        # Summarize intersected Land Ownership by Owner and total Acres
        arcpy.Statistics_analysis(pip_lo_in_buffer_shp, pip_lo_in_buf_sum_dbf, "Acres SUM", "OWNER")
        arcpy.MakeTableView_management(pip_lo_in_buf_sum_dbf)
        add3sigmaLoSumTbl = arcpy.mapping.TableView(pip_lo_in_buf_sum_dbf)
        arcpy.mapping.AddTableView(dataframe, add3sigmaLoSumTbl)

        # Symbolize and Refresh
        lo_layer = arcpy.mapping.ListLayers(mxd, "*Land Ownership within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, lo_layer, sourceLoSymbologyLayer, True)
        lo_layer.symbology.addAllValues()

        pip_layer = arcpy.mapping.ListLayers(mxd, "*Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, pip_layer, sourcePipSymbologyLayer, True)

        rr_layer = arcpy.mapping.ListLayers(mxd, "*Range Rings*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, rr_layer, sourceRrsSymbologyLayer, True)

        pop_layer = arcpy.mapping.ListLayers(mxd, "*Populated Places*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, pop_layer, sourcePopSymbologyLayer, True)

        afs_layer = arcpy.mapping.ListLayers(mxd, "*Known Sites*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, afs_layer, sourceAfsSymbologyLayer, True)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

        # Populate Mission GDB
        mission_layers = [pip_point_3338, pip_lo_in_buffer_shp, pip_popn_places_in_buffer_shp, pip_range_rings_shp, pip_known_sites_in_buffer_shp]
        arcpy.FeatureClassToGeodatabase_conversion(mission_layers, arcpy.env.workspace)



        return
