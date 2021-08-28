import arcpy
from arcpy import env

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PFRRtools"
        self.alias = "PFRR Tools"

        # List of tool classes associated with this toolbox
        self.tools = [PFRR]

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
        param2.value = 20

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
        arcpy.env.workspace = "C:/gina/poker/pip"
        arcpy.env.overwriteOutput = True
        adnr_lo_shp = "C:/gina/poker/shp/wip/land_ownership_data/adnr_gls_dls_merge_20170823_v1.shp"
        pfrr_popn_places = "C:/gina/poker/shp/wip/popn_places_data/pokerflat_popn_places_gcs_wgs84_to_akalbers_2.shp"
        pipTable = "C:/gina/poker/dbf/predicted_impact_xy.dbf"
        pip_point_shp = "C:/gina/poker/pip/pip_point.shp"
        pip_point_3338 = "C:/gina/poker/pip/pip_point_3338.shp"
        pip_buffer_shp = "C:/gina/poker/pip/pip_buffer.shp"
        pip_lo_in_buffer_shp = "C:/gina/poker/pip/pip_lo_in_buffer.shp"
        pip_lo_in_buf_sum_dbf = "C:/gina/poker/pip/pip_lo_in_buf_sum.dbf"
        pip_lo_in_buf_sum_csv = "C:/gina/poker/pip/pip_lo_in_buf_sum.csv"
        pip_popn_places_in_buffer_shp = "C:/gina/poker/pip/pip_popn_places_in_buffer.shp"
        x = parameters[0].valueAsText
        y = parameters[1].valueAsText
        r = parameters[2].valueAsText + " NauticalMiles"
        pipLayer = "pipLayer1"
        srs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")
        intersect_fc1 = [adnr_lo_shp, pip_buffer_shp]
        intersect_fc2 = [pfrr_popn_places, pip_buffer_shp]
        mxd = arcpy.mapping.MapDocument("current")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
        sourceLoSymbologyLayer = arcpy.mapping.Layer("C:/gina/poker/lyr/lo2.lyr")
        sourcePipSymbologyLayer = arcpy.mapping.Layer("C:/gina/poker/lyr/pip.lyr")


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
        arcpy.Intersect_analysis(intersect_fc1, pip_lo_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Intersect pip buffer with popn places
        arcpy.Intersect_analysis(intersect_fc2, pip_popn_places_in_buffer_shp, "ALL", "", "INPUT")

        # Process: Make feature layers and add to the map
        ## pip feature class list
        fclist = arcpy.ListFeatureClasses()

        ## pip layer
        arcpy.MakeFeatureLayer_management(pip_point_3338, "Predicted Impact Point")

        ## land ownership layer
        arcpy.MakeFeatureLayer_management(pip_lo_in_buffer_shp, "Land Ownership within 3sigma of Predicted Impact Point")

        ## populated places layer
        popn_places_records = int(arcpy.GetCount_management(pip_popn_places_in_buffer_shp).getOutput(0))
        if popn_places_records > 0:
            arcpy.MakeFeatureLayer_management(pip_popn_places_in_buffer_shp, "Populated Places within 3sigma of Predicted Impact Point")
            addPipPopnPlacesLayer = arcpy.mapping.Layer("Populated Places within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipPopnPlacesLayer)

        addPipPointLayer = arcpy.mapping.Layer("Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, addPipPointLayer)

        add3sigmaLoLayer = arcpy.mapping.Layer("Land Ownership within 3sigma of Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, add3sigmaLoLayer)



        # Add and calc Acres field for intersected Land Ownership
        arcpy.AddField_management(pip_lo_in_buffer_shp, "Acres", "DOUBLE")
        arcpy.CalculateField_management(pip_lo_in_buffer_shp, "Acres", "!shape.area@acres!", "PYTHON_9.3", "")

        # Summarize intersected Land Ownership by Owner and total Acres
        arcpy.Statistics_analysis(pip_lo_in_buffer_shp, pip_lo_in_buf_sum_dbf, "Acres SUM", "OWNER")
        # arcpy.MakeTableView_management(pip_lo_in_buf_sum_dbf)
        add3sigmaLoSumTbl = arcpy.mapping.TableView(pip_lo_in_buf_sum_dbf)
        arcpy.mapping.AddTableView(dataframe, add3sigmaLoSumTbl)

        # Symbolize and Refresh
        lo_layer = arcpy.mapping.ListLayers(mxd, "*Land Ownership within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, lo_layer, sourceLoSymbologyLayer, True)
        lo_layer.symbology.addAllValues()

        pip_layer = arcpy.mapping.ListLayers(mxd, "*Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, pip_layer, sourcePipSymbologyLayer, True)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

        return
