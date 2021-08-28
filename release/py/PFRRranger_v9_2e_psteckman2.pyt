import arcpy
import math
import os
import sys
import tempfile

from arcpy import env

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
        self.label = "Ending_Point"
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

        param5 = arcpy.Parameter(
            displayName="Distance (in Kilometers)",
            name="Distance",
            datatype="GPDouble",
            parameterType="Optional",
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
        param5.value = float(param2.valueAsText)
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

        report_h = open(report,"w")
        report_h.write("Starting Point Latitude: " + str(latit_sp))
        report_h.write("\nStarting Point Longitude: " + str(longit_sp))
        report_h.write("\nYour Range in Kilometers: " + str(distance))
        report_h.write("\nYour Azimuth in Degrees: " + str(azi))
        report_h.write("\nEnding Point Latitude: " + str(lat_ep))
        report_h.write("\nEnding Point Latitude: " + str(long_ep))
        report_h.close()

        return

class Range_Distance(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Oblate Tools"
        self.description = "This tool calculates the range and bearing between" + \
        "two points (initial point and final point) if given the initial point, " + \
        "range and bearing."
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
            displayName="Final Point Lon (in Decimal Degrees)",
            name="fplon",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        param3 = arcpy.Parameter(
            displayName="Final Point Lat (in Decimal Degrees)",
            name="fplat",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Report",
            name="Repfile",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

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
        param0.value = ""         # pfrr lon
        param1.value = ""         # pfrr lat
        param2.value = ""         # pip lon
        param3.value = ""         # pip lat
        param4.value = ""         # Report Name

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

        latit_ep = float(parameters[3].valueAsText)
        longit_ep = float(parameters[2].valueAsText)
        deg_to_rad = math.pi/180

        delta_lat = math.fabs(latit_ep-float(parameters[1].valueAsText))
        delta_long = math.fabs(longit_ep-float(parameters[0].valueAsText))
        #Math used to calculate the distance between two points
        a = (math.sin(deg_to_rad*delta_lat/2)**2) + math.cos(deg_to_rad*float(parameters[1].valueAsText))*math.cos(deg_to_rad*latit_ep)*(math.sin(deg_to_rad*delta_long/2)**2)
        c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
        distance = 6371*c

        #Math used to calculate the azimuth between two points
        p1 = math.sin(delta_long*deg_to_rad)*math.cos(latit_ep*deg_to_rad)
        p2 = math.cos(float(parameters[1].valueAsText)*deg_to_rad)*math.sin(latit_ep*deg_to_rad)
        p3 = math.sin(float(parameters[1].valueAsText)*deg_to_rad)*math.cos(latit_ep*deg_to_rad)*math.cos(delta_long*deg_to_rad)
        azimuth = math.atan2(p1,p2-p3)
        azimuth = azimuth *(180.0/math.pi)
        azimuth = (azimuth+360)%360

        outshp = os.path.splitext(parameters[4])[0]+ '.txt'

        report = open(parameters[4].valueAsText,"w")
        report.write("Starting Point Latitude: " + str(float(parameters[1])))
        report.write("Starting Point Longitude: " + str(float(parameters[0])))
        report.write("Your Range in Kilometers: " + str(distance))
        report.write("Your Azimuth in Degrees: " + str(azimuth))
        report.write("Ending Point Latitude: " + str(latit_ep))
        report.write("Ending Point Latitude: " + str(longit_ep))
        report.close()

        return


class PFRR(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "PFRR Ranger"
        self.description = "This tool plots the predicted impact point (Lon,Lat) " + \
        "then calculates a 3sigma cirlce centered on the predicted impact point, and " + \
        "intersects the circle with underlying Land Ownership to output a new " + \
        "land_ownership_within_3sigma layer in the map"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input Lon (in Decimal Degrees)",
            name="lon",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Input Lat (in Decimal Degrees)",
            name="lat",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Input 3sigma Cirlce Radius (in Nautical Miles)",
            name="radius",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

##        # Fourth param
##        param3 = arcpy.Parameter(
##            displayName="Slurp"
##            name="slurp"
##            datatype="GPFeatureLayer"
##            parameterType="Derived"
##            direction="Output")

        # param2.parameterDependencies = [param0.name]
        # param2.schema.clone = True

        params = [param0, param1, param2]
        param0.value = -149.906682
        param1.value = 67.264536
        param2.value = 21

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

        # local variables and env
    #    arcpy.env.workspace = "E:/gina/poker/pip"
    #    arcpy.env.overwriteOutput = True
    #    adnr_lo_shp = "E:/gina/poker/shp/wip/land_ownership_data/adnr_gls_dls_merge_20170823_v1.shp"
    #    pfrr_popn_places = "E:/gina/poker/shp/wip/popn_places_data/pokerflat_popn_places_gcs_wgs84_to_akalbers_2.shp"
    #    pipTable = "E:/gina/poker/dbf/predicted_impact_xy.dbf"
    #    pip_point_shp = "E:/gina/poker/pip/pip_point.shp"
    #    pip_point_3338 = "E:/gina/poker/pip/pip_point_3338.shp"
    #    pip_buffer_shp = "E:/gina/poker/pip/pip_buffer.shp"
    #    pip_range_rings_shp = "E:/gina/poker/pip/pip_range_rings.shp"
    #    pip_lo_in_buffer_shp = "E:/gina/poker/pip/pip_lo_in_buffer.shp"
    #    pip_lo_in_buf_sum_dbf = "E:/gina/poker/pip/pip_lo_in_buf_sum.dbf"
    #    pip_lo_in_buf_sum_csv = "E:/gina/poker/pip/pip_lo_in_buf_sum.csv"
    #    pip_popn_places_in_buffer_shp = "E:/gina/poker/pip/pip_popn_places_in_buffer.shp"
    #    x = parameters[0].valueAsText
    #    y = parameters[1].valueAsText
    #    r = parameters[2].valueAsText + " NauticalMiles"
    #    rr1 = (float(parameters[2].valueAsText))/3
    #    rr2 = (rr1*2)
    #    rrs = str(rr1) + ";" + str(rr2) + ";" + r.split(" ")[0]
    #    pipLayer = "pipLayer1"
    #    srs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")
    #    intersect_fc1 = [adnr_lo_shp, pip_buffer_shp]
    #    intersect_fc2 = [pfrr_popn_places, pip_buffer_shp]
    #    mxd = arcpy.mapping.MapDocument("current")
    #    dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
    #    sourceLoSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/lo2.lyr")
    #    sourcePipSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/pip2.lyr")
    #    sourceRrsSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/rrs.lyr")


        # Process: Calculate Lon Field
    #    arcpy.CalculateField_management(pipTable, "Lon", x, "PYTHON", "")

        # Process: Calculate Lat Field
    #    arcpy.CalculateField_management(pipTable, "Lat", y, "PYTHON", "")

        # Process: Make XY Event Layer
    #    arcpy.MakeXYEventLayer_management(pipTable, "Lon", "Lat", pipLayer, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "")

        # Process: Copy Features
    #    arcpy.CopyFeatures_management(pipLayer, pip_point_shp, "", "0", "0", "0")

        # Process: Project pip point
    #    arcpy.Project_management(pip_point_shp, pip_point_3338, srs)

        # Process: Buffer pip point
    #    arcpy.Buffer_analysis(pip_point_3338, pip_buffer_shp, r, "FULL", "ROUND", "NONE", "", "PLANAR")

        # Process: Multiple Ring Buffer
    #    arcpy.MultipleRingBuffer_analysis(pip_point_3338, pip_range_rings_shp, rrs, "NauticalMiles", "", "NONE", "FULL")

        # Process: Intersect pip buffer with land ownership
    #    arcpy.Intersect_analysis(intersect_fc1, pip_lo_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Intersect pip buffer with popn places
    #    arcpy.Intersect_analysis(intersect_fc2, pip_popn_places_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Make feature layers and add to the map
        ## pip feature class list
    #    fclist = arcpy.ListFeatureClasses()

        ## pip layer
    #    arcpy.MakeFeatureLayer_management(pip_point_3338, "Predicted Impact Point")

        ## land ownership layer
    #    arcpy.MakeFeatureLayer_management(pip_lo_in_buffer_shp, "Land Ownership within 3sigma of Predicted Impact Point")

        ## Range Rings
    #    arcpy.MakeFeatureLayer_management(pip_range_rings_shp, "Range Rings")

        ## populated places layer
    #    popn_places_records = int(arcpy.GetCount_management(pip_popn_places_in_buffer_shp).getOutput(0))
    #    if popn_places_records > 0:
    #        arcpy.MakeFeatureLayer_management(pip_popn_places_in_buffer_shp, "Populated Places within 3sigma of Predicted Impact Point")
    #        addPipPopnPlacesLayer = arcpy.mapping.Layer("Populated Places within 3sigma of Predicted Impact Point")
    #        arcpy.mapping.AddLayer(dataframe, addPipPopnPlacesLayer)

    #    addPipPointLayer = arcpy.mapping.Layer("Predicted Impact Point")
    #    arcpy.mapping.AddLayer(dataframe, addPipPointLayer)

    #    add3sigmaLoLayer = arcpy.mapping.Layer("Land Ownership within 3sigma of Predicted Impact Point")
    #    arcpy.mapping.AddLayer(dataframe, add3sigmaLoLayer)

    #    addRangeRings = arcpy.mapping.Layer("Range Rings")
    #    arcpy.mapping.AddLayer(dataframe, addRangeRings)


        # Add and calc Acres field for intersected Land Ownership
    #    arcpy.AddField_management(pip_lo_in_buffer_shp, "Acres", "DOUBLE")
    #    arcpy.CalculateField_management(pip_lo_in_buffer_shp, "Acres", "!shape.area@acres!", "PYTHON_9.3", "")

        # Summarize intersected Land Ownership by Owner and total Acres
    #    arcpy.Statistics_analysis(pip_lo_in_buffer_shp, pip_lo_in_buf_sum_dbf, "Acres SUM", "OWNER")
        # arcpy.MakeTableView_management(pip_lo_in_buf_sum_dbf)
    #    add3sigmaLoSumTbl = arcpy.mapping.TableView(pip_lo_in_buf_sum_dbf)
    #    arcpy.mapping.AddTableView(dataframe, add3sigmaLoSumTbl)

        # Symbolize and Refresh
    #    lo_layer = arcpy.mapping.ListLayers(mxd, "*Land Ownership within 3sigma of Predicted Impact Point*", dataframe)[0]
    #    arcpy.mapping.UpdateLayer(dataframe, lo_layer, sourceLoSymbologyLayer, True)
    #    lo_layer.symbology.addAllValues()

    #    pip_layer = arcpy.mapping.ListLayers(mxd, "*Predicted Impact Point*", dataframe)[0]
    #    arcpy.mapping.UpdateLayer(dataframe, pip_layer, sourcePipSymbologyLayer, True)

    #    rr_layer = arcpy.mapping.ListLayers(mxd, "*Range Rings*", dataframe)[0]
    #    arcpy.mapping.UpdateLayer(dataframe, rr_layer, sourceRrsSymbologyLayer, True)

    #    arcpy.RefreshTOC()
    #    arcpy.RefreshActiveView()

        return
