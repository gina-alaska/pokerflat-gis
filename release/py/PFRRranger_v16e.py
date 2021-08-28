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

    a = 6378137.0
    b = 6356752.314140356

    f = (a-b)/a

    longit_sp = math.radians(longit_sp)
    latit_sp = math.radians(latit_sp)
    latit_ep = math.radians(latit_ep)
    longit_ep = math.radians(longit_ep)

    L = longit_ep-longit_sp
    tanU1 = (1-f) * math.tan(p1lat)
    cosU1 = 1 / math.sqrt(1+(tanU1*tanU1))
    sinU1 = tanU1 * cosU1
    tanU2 = (1-f) * math.tan(p2lat)
    cosU2 = 1 / math.sqrt(1+(tanU2*tanU2))
    sinU2 = tanU2 * cosU2

    lamda = L
    lamda_tick = 0
    iterations = 0

    while True:
        sinlamda = math.sin(lamda)
        coslamda = math.cos(lamda)
        sinSqsigma = (cosU2*sinlamda) * (cosU2*sinlamda) + ((cosU1*sinU2) - (sinU1*cosU2*coslamda)) * ((cosU1*sinU2) - (sinU1*cosU2*coslamda))
        if sinSqsigma == 0:
            break
        sinsigma = math.sqrt(sinSqsigma)
        cossigma = (sinU1*sinU2)+(cosU1*cosU2*coslamda)
        sigma = math.atan2(sinsigma, cossigma)
        sinalpha = cosU1*cosU2*sinlamda/sinsigma
        cosSqalpha = 1 - (sinalpha*sinalpha)
        cos2sigmaM = cossigma - (2*sinU1*sinU2 / cosSqalpha)
        if cos2sigmaM == None:
            cos2sigmaM = 0
        C = f/16*cosSqalpha*(4+f*(4-3*cosSqalpha))
        lamda_tick = lamda
        lamda = L + (1-C) * f * sinalpha * (sigma + C*sinsigma*(cos2sigmaM+C*cossigma*(-1+2*cos2sigmaM*cos2sigmaM)))
        iterations = iterations + 1
        if math.fabs(lamda-lamda_tick)>1e-12 and iterations<100:
            break

    uSq = cosSqalpha * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltasigma = B*sinsigma*(cos2sigmaM+B/4*(cossigma*(-1+2*cos2sigmaM*cos2sigmaM)-B/6*cos2sigmaM*(-3+4*sinsigma*sinsigma)*(-3+4*cos2sigmaM*cos2sigmaM)))
    s = b*A*(sigma-deltasigma)

    intialbearing = math.atan2(cosU2*sinlamda, (cosU1*sinU2)-(sinU1*cosU2*coslamda))

    intialbearing = (intialbearing + 2*math.pi) % (2*math.pi)

    intialbearing = math.degrees(intialbearing)

    return [s, intialbearing]

# Convert units
def convertUnits(v, unit):
    #rng = float(cval)
    val = float(v)
    if unit == "Miles":
        r = val*0.6213711922
    elif unit == "Nautical Miles (U.S.)":
        r = (val*0.6213711922)/1.15077945  # Represents US and International Nautical Mile = 1852 meters exactly
    elif unit == "Yards":
        r = val*1093.613298
    elif unit == "Inches":
        r = val*39370.07874
    elif unit == "Meters":
        r = val*1000.0
    elif unit == "Feet (U.S. Survey)":
        r = (val*1000.0)*3.28083333333  # Feet to Meters *0.304800609601
    elif unit == "Feet":
        r = val*3280.839895
    elif unit == "Rods":
        r = (val*1000.0)*0.1988384
    elif unit == "Chains":
        r = (val*1000.0)*0.0497096
    else:
        r = val

    return r

# Convert to Km
def convert2km(lUnit):
    dist = float(lUnit.split(" ")[0])
    units = lUnit.split(" ")[1]

    if units == "Kilometers":
        km = dist
    elif units == "Meters":
        km = dist/1000
    elif units == "Miles":
        km = dist*1.609344
    elif units == "Yards":
        km = dist*0.0009144
    elif units == "Feet":
        km = dist*0.0003048
    elif units == "NauticalMiles":
        km = dist*1.852
    else:
        km = 0

    return km

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PFRR Tools"
        self.alias = "PFRR Tools"

        # List of tool classes associated with this toolbox
        self.tools = [unitConversion, Ending_Point, Range_Distance, PFRR]

class unitConversion(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4) Convert Units"
        self.description ="Tool for testing unit conversions"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        """Define parameter definitions"""


        # Ninth param - Range
        param0 = arcpy.Parameter(
            displayName="Range (Kilometers)",
            name="km",
            datatype="GPVariant",
            parameterType="Optional",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName='Linear Unit',
            name='unit',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        param2 = arcpy.Parameter(
            displayName='Conversion Result',
            name='result',
            datatype='GPDouble',
            parameterType='Optional',
            direction='Input')

        params = [param0, param1, param2]

        # Default disabled params
        param1.enabled = 0
        param2.enabled = 0

        # Param Dependencies
##        param3.parameterDependencies = [param0.name]
##        param3.columns = [['From', 'To'], ['GPString', 'GPString']]
##        param3.filters[1].type = 'ValueList'
##        param3.values = [['Kilometers', 'Miles']]
##        param3.filters[1].list = ['Miles', 'Kilometers', 'Feet', 'Meters', 'Rods']

        # Default param values
        param0.value = 0
        param1.value = "Kilometers"
        param1.filter.type = "ValueList"
        param1.filter.list = ['Kilometers', 'Meters', 'Miles', 'Nautical Miles (U.S.)', 'Yards', 'Feet', 'Feet (U.S. Survey)', 'Inches', 'Rods', 'Chains']

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if not parameters[0].altered:
            parameters[1].enabled = 0
            parameters[2].enabled = 0
            #parameters[2].value = parameters[0].valueAsText
        else:
            parameters[1].enabled = 1
            parameters[2].enabled = 1
            parameters[2].value = parameters[0].valueAsText
            if parameters[1].altered:
                v = convertUnits(parameters[0].valueAsText, parameters[1].valueAsText)
                parameters[2].value = v






        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return

class Ending_Point(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3) Ending Point"
        self.description = "This tool calculates the final point given" + \
        "the initial point, range and bearing. Click OK to plot geometry."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Enter as DMS",
            name="dms",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Starting Point Longitude (in Decimal Degrees)",
            name="splon",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Starting Point Latitude (in Decimal Degrees)",
            name="splat",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName = "Start Point Longitude - Degrees Minutes Seconds - (Enter West as negative degrees)",
            name = "dmsSpLon",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        param4 = arcpy.Parameter(
            displayName = "Start Point Latitude - Degrees Minutes Seconds",
            name = "dmsSpLat",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        param5 = arcpy.Parameter(
            displayName="Distance",
            name="Distance",
            datatype="GPLinearUnit",
            parameterType="Optional",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Direction (Degrees Azimuth)",
            name="Azimuth",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Ending Point Lon (Decimal Degrees)",
            name="elon",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param8 = arcpy.Parameter(
            displayName="Ending Point Lat (Decimal Degrees)",
            name="elat",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8]

        # Default enabled params
        param3.enabled = 0
        param4.enabled = 0
        param7.enabled = 0
        param8.enabled = 0

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
                    parameters[3].value = str(int(dx1)) + " " + str(int(mx1)) + " " + str(sx1)

            if parameters[2].altered:   # Start DD Lat
                ddy1 = parameters[2].valueAsText
                dy1 = ddy1.split(".")[0]
                # parameters[7].value = dy
                my1 = (float(ddy1) - float(dy1))*60
                # parameters[8].value = int(my)
                sy1 = round((my1 - int(str(my1).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[4].value = str(int(dy1)) + " " + str(int(my1)) + " " + str(sy1)

        if parameters[0].altered:
            if parameters[0].value:
                parameters[1].enabled = 0
                parameters[2].enabled = 0
                parameters[3].enabled = 1
                parameters[4].enabled = 1

                if parameters[3].altered:   # Start DMS Lon
                    degx1 = int(parameters[3].valueAsText.split(" ")[0])*-1
                    minx1 = float(parameters[3].valueAsText.split(" ")[1])
                    secx1 = float(parameters[3].valueAsText.split(" ")[2])
                    parameters[1].value = (degx1 + (minx1/60 + secx1/3600))*-1

                if parameters[4].altered:   # Start DMS Lat
                    degy1 = int(parameters[4].valueAsText.split(" ")[0])
                    miny1 = float(parameters[4].valueAsText.split(" ")[1])
                    secy1 = float(parameters[4].valueAsText.split(" ")[2])
                    parameters[2].value = degy1 + (miny1/60 + secy1/3600)

            else:                           # DMS checked then unchecked
                parameters[1].enabled = 1
                parameters[2].enabled = 1
                parameters[3].enabled = 0
                parameters[4].enabled = 0

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
                    parameters[3].value = str(int(dx1)) + " " + str(int(mx1)) + " " + str(sx1)

            if parameters[2].altered:   # Start DD Lat
                ddy1 = parameters[2].valueAsText
                dy1 = ddy1.split(".")[0]
                # parameters[7].value = dy
                my1 = (float(ddy1) - float(dy1))*60
                # parameters[8].value = int(my)
                sy1 = round((my1 - int(str(my1).split(".")[0]))*60, 6)
                # parameters[9].value = sy
                parameters[4].value = str(int(dy1)) + " " + str(int(my1)) + " " + str(sy1)

##        if parameters[5].altered:
##            Km = convert2km(parameters[5].valueAsText)
##            parameters[8].value = Km

        if parameters[1].value and parameters[2].value and parameters[5].value and parameters[6].value:
            # Calculate angular distance
            Km = convert2km(parameters[5].valueAsText)
            adist = Km/6380     # 6356.752 at poles vs 6371.001 ave = radius of the Earth https://rechneronline.de/earth-radius/

            # Calculate the ending point lat      https://www.movable-type.co.uk/scripts/latlong.html
            p1 = math.sin(math.radians(float(parameters[2].valueAsText)))*math.cos(adist)
            p2 = math.cos(math.radians(float(parameters[2].valueAsText)))*math.sin(adist)*math.cos(math.radians(float(parameters[6].valueAsText)))
            lat2 = math.degrees(math.asin(p1+p2))
            parameters[8].enabled = 1
            parameters[8].value = lat2

            # Calculate the ending point longitude
            p3 = math.sin(math.radians(float(parameters[6].valueAsText)))*math.sin(adist)*math.cos(math.radians(float(parameters[2].valueAsText)))
            p4 = math.cos(adist) - (math.sin(math.radians(float(parameters[2].valueAsText)))*math.sin(math.radians(lat2)))
            lon2 = float(parameters[1].valueAsText) + math.degrees(math.atan2(p3,p4))
            parameters[7].enabled = 1
            parameters[7].value = lon2


        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # local vars and env
        arcpy.env.overwriteOutput = True
        epPoint_dbf = "E:/gina/poker/dbf/ep_info.dbf"
        epPointGcs_shp = "E:/gina/poker/scratch/epPointGcs.shp"
        #epPoint3338_shp = "E:/gina/poker/scratch/epPoint3338.shp"
        #epPointLyr = "epPointLyr1"
        #epTgtSrs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")
        epLine_shp = "E:/gina/poker/scratch/epLine.shp"
        epLineLyr = "epLineLyr1"
        #fpPoint_shp = "E:/gina/poker/scratch/fpPoint.shp"
        #fpPointLyr = "fpPointLyr1"
        x = parameters[1].valueAsText
        y = parameters[2].valueAsText
        r = convert2km(parameters[5].valueAsText)*1000
        a = parameters[6].valueAsText
        #sp_symb = arcpy.mapping.Layer("E:/gina/poker/lyr/sp.lyr")
        ln_symb = arcpy.mapping.Layer("E:/gina/poker/lyr/ln.lyr")
        #fp_symb = arcpy.mapping.Layer("E:/gina/poker/lyr/fp.lyr")
        mxd = arcpy.mapping.MapDocument("current")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]

        # Process: Calculate Lon Field
        arcpy.CalculateField_management(epPoint_dbf, "Lon", x, "PYTHON", "")

        # Process: Calculate Lat Field
        arcpy.CalculateField_management(epPoint_dbf, "Lat", y, "PYTHON", "")

        # Process: Calculate Bearing Field
        arcpy.CalculateField_management(epPoint_dbf, "Bearing", a, "PYTHON", "")

        # Process: Calculate Distance Field
        arcpy.CalculateField_management(epPoint_dbf, "Distance", r, "PYTHON", "")

        # Process: Make XY Event Layer
        #arcpy.MakeXYEventLayer_management(epPoint_dbf, "Lon", "Lat", epPointLyr, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "")

        # Process: Copy Features
        #arcpy.CopyFeatures_management(epPointLyr, epPointGcs_shp, "", "0", "0", "0")

        # Process: Project pip point
        #arcpy.Project_management(epPointGcs_shp, epPoint3338_shp, epTgtSrs)

        #arcpy.MakeFeatureLayer_management(epPoint3338_shp, "Start Point")

        #add_epPointLayer = arcpy.mapping.Layer("Start Point")
        #arcpy.mapping.AddLayer(dataframe, add_epPointLayer)

        #epPointLyr = arcpy.mapping.ListLayers(mxd, "*Start Point*", dataframe)[0]
        #arcpy.mapping.UpdateLayer(dataframe, epPointLyr, sp_symb, True)

        # Process: Bearing-Distance To Line & Add Geometry Attr - Line Start, Mid and End Coords
        arcpy.BearingDistanceToLine_management(epPoint_dbf, epLine_shp, "Lon", "Lat", "Distance", "METERS", "Bearing", "DEGREES", "GEODESIC")
        arcpy.AddGeometryAttributes_management(epLine_shp, "LINE_START_MID_END")

        # Process: Make ep line layer
        arcpy.MakeFeatureLayer_management(epLine_shp, "Bearing-Distance Line")

        add_epLineLayer = arcpy.mapping.Layer("Bearing-Distance Line")
        arcpy.mapping.AddLayer(dataframe, add_epLineLayer)

        epLineLyr = arcpy.mapping.ListLayers(mxd, "*Bearing-Distance Line*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, epLineLyr, ln_symb, True)

        # Process: Make XY Event Layer - Start Point
        #arcpy.MakeXYEventLayer_management(epLine_shp, "Lon", "Lat", epPointLyr, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "")

        # Process: Feature Vertex to Point (generates ending point)
        #arcpy.FeatureVerticesToPoints_management(epLine3338_shp, fpPoint_shp, "END")

        # Process: Make fp point layer
        #arcpy.MakeFeatureLayer_management(fpPoint_shp, "End Point")

        #add_fpPointLayer = arcpy.mapping.Layer("End Point")
        #arcpy.mapping.AddLayer(dataframe, add_fpPointLayer)

        #fpPointLyr = arcpy.mapping.ListLayers(mxd, "*End Point*", dataframe)[0]
        #arcpy.mapping.UpdateLayer(dataframe, fpPointLyr, fp_symb, True)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

        return


class Range_Distance(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2) Bearing and Range"
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

        # Ninth param - Azimuth
        param9 = arcpy.Parameter(
            displayName="Bearing (Degrees Azimuth)",
            name="az",
            datatype="GPVariant",
            parameterType="Optional",
            direction="Input")

        # Tenth param - Range
        param10 = arcpy.Parameter(
            displayName="Range (Kilometers)",
            name="km",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        # Eleventh param - Unit Conversion
        param11 = arcpy.Parameter(
            displayName='Convert Linear Units to: ',
            name='unit',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # Twelvth param - Conversion Result
        param12 = arcpy.Parameter(
            displayName='Conversion Result',
            name='result',
            datatype='GPDouble',
            parameterType='Optional',
            direction='Input')


        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12]

        # Default disabled params
        param5.enabled = 0
        param6.enabled = 0
        param7.enabled = 0
        param8.enabled = 0
        param9.enabled = 0
        param10.enabled = 0
        param11.enabled = 0
        param12.enabled = 0

        # Default param values
        param11.value = "Kilometers"
        param11.filter.type = "ValueList"
        param11.filter.list = ['Kilometers', 'Meters', 'Miles', 'Nautical Miles (U.S.)', 'Yards', 'Feet', 'Feet (U.S. Survey)', 'Inches', 'Rods', 'Chains']

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

#######  Update for modified params 9, 10, 11, and 12  #######

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
                parameters[9].enabled = 1
                parameters[9].value = str(round(rd[1],5)) + u'\xb0'
                parameters[10].enabled = 1
                parameters[10].value = str(round(rd[0],5))
                parameters[11].enabled = 1
                if parameters[11].altered:
                    parameters[12].enabled = 1
                    parameters[12].value = convertUnits(parameters[10].valueAsText, parameters[11].valueAsText)






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
                    parameters[9].enabled = 1
                    parameters[9].value = str(round(rd[1],5)) + u'\xb0'
                    parameters[10].enabled = 1
                    parameters[10].value = str(round(rd[0],5))
                    parameters[11].enabled = 1
                    if parameters[11].altered:
                        parameters[12].enabled = 1
                        parameters[12].value = convertUnits(parameters[10].valueAsText, parameters[11].valueAsText)

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
                    parameters[9].enabled = 1
                    parameters[9].value = str(round(rd[1],5)) + u'\xb0'
                    parameters[10].enabled = 1
                    parameters[10].value = str(round(rd[0],5))
                    parameters[11].enabled = 1
                    if parameters[11].altered:
                        parameters[12].enabled = 1
                        parameters[12].value = convertUnits(parameters[10].valueAsText, parameters[11].valueAsText)

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
        afs_known_sites = "E:/gina/poker/shp/afs_data/asf_known_sites_20180629_3338.shp"
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
