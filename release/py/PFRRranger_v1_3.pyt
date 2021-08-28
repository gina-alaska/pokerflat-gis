import arcpy
from arcpy import env

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PFRRtools"
        self.alias = "PFRR Tools"

        # List of tool classes associated with this toolbox
        self.tools = [Tool, PFRR]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
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
            displayName="Input 3sigma Cirlce Radius (in Miles)",
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
        param0.value = -148.480679
        param1.value = 68.180358
        param2.value = 4

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
        arcpy.env.workspace = "E:/gina/poker/pip"
        adnr_lo_shp = "E:/gina/poker/shp/wip/adnr_gls_dls_merge_20170823_v1.shp"
        pipTable = "E:/gina/poker/dbf/predicted_impact_xy.dbf"
        pip_point_shp = "E:/gina/poker/pip/pip_point.shp"
        pip_point_3338 = "E:/gina/poker/pip/pip_point_3338.shp"
        pip_buffer_shp = "E:/gina/poker/pip/pip_buffer.shp"
        pip_lo_in_buffer_shp = "E:/gina/poker/pip/pip_lo_in_buffer.shp"
        x = parameters[0].valueAsText
        y = parameters[1].valueAsText
        r = parameters[2].valueAsText + " Miles"
        pipLayer = "pipLayer"
        srs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")
        intersect_fc = [adnr_lo_shp, pip_buffer_shp]
        mxd = arcpy.mapping.MapDocument("current")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
        sourceSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/shp/wip/adnr_gls_dls_merge_20170823_v2.lyr")



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

        # Process: Intersect pip buffer with land ownership
        arcpy.Intersect_analysis(intersect_fc, pip_lo_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Make feature layers and add to the map
        arcpy.MakeFeatureLayer_management(pip_point_3338, "Predicted Impact Point")
        arcpy.MakeFeatureLayer_management(pip_lo_in_buffer_shp, "Land Onwership within 3sigma of Predicted Impact Point")
        addPipPointLayer = arcpy.mapping.Layer("Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, addPipPointLayer)
        add3sigmaLoLayer = arcpy.mapping.Layer("Land Onwership within 3sigma of Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, add3sigmaLoLayer)

        layers = arcpy.mapping.ListLayers(mxd)
        arcpy.mapping.UpdateLayer(dataframe, layers[1], sourceSymbologyLayer, True)
        layers[1].symbology.addAllValues()

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

        return
