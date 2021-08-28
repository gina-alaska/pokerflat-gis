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
        ## workspace
        arcpy.env.workspace = "E:/gina/poker/pip"

        ## source data
        adnr_lo_shp = "E:/gina/poker/shp/wip/land_ownership_data/adnr_gls_dls_merge_20170823_v1.shp"
        pfrr_popn_places = "E:/gina/poker/shp/wip/popn_places_data/pokerflat_popn_places_gcs_wgs84_to_akalbers_2.shp"
        dot_rds = "E:/gina/poker/shp/asgdc_data/mv_dot_centerline_route_ln.shp"
        infra_trails = "E:/gina/poker/shp/asgdc_data/mv_infra_trail_ln.shp"
        rs2477_trails = "E:/gina/poker/shp/asgdc_data/mv_rs2477_ln.shp"
        infra_airstrips = "E:/gina/poker/shp/asgdc_data/mv_infra_airstrip_pt.shp"
        runways = "E:/gina/poker/shp/asgdc_data/mv_airport_runway_pt.shp"

        ## pip seed table
        pipTable = "E:/gina/poker/dbf/predicted_impact_xy.dbf"

        ## pip output data
        pip_point_shp = "E:/gina/poker/pip/pip_point.shp"
        pip_point_3338 = "E:/gina/poker/pip/pip_point_3338.shp"
        pip_buffer_shp = "E:/gina/poker/pip/pip_buffer.shp"
        pip_lo_in_buffer_shp = "E:/gina/poker/pip/pip_lo_in_buffer.shp" # 1
        pip_lo_in_buf_sum_dbf = "E:/gina/poker/pip/pip_lo_in_buf_sum.dbf"
        pip_lo_in_buf_sum_csv = "E:/gina/poker/pip/pip_lo_in_buf_sum.csv"
        pip_popn_places_in_buffer_shp = "E:/gina/poker/pip/pip_popn_places_in_buffer.shp" # 2
        pip_roads_in_buffer_shp = "E:/gina/poker/pip/pip_roads_in_buffer.shp" # 3
        pip_rs2477_in_buffer_shp = "E:/gina/poker/pip/pip_rs2477_in_buffer.shp" # 4
        pip_infra_trails_in_buffer_shp = "E:/gina/poker/pip/pip_infra_trails_in_buffer.shp" # 5
        pip_infra_airstrips_in_buffer_shp = "E:/gina/poker/pip/pip_infra_airstrips_in_buffer.shp" # 6
        pip_runways_in_buffer_shp = "E:/gina/poker/pip/pip_runways_in_buffer.shp" # 7
        pipLayer = "pipLayer"

        ## pip buffer params
        x = parameters[0].valueAsText
        y = parameters[1].valueAsText
        r = parameters[2].valueAsText + " NauticalMiles"

        ## target coord sys
        srs = arcpy.SpatialReference("Alaska Albers Equal Area Conic")

        ## intersect arrays
        intersect_lo = [adnr_lo_shp, pip_buffer_shp]  # 1
        intersect_pp = [pfrr_popn_places, pip_buffer_shp] # 2
        intersect_rd = [dot_rds, pip_buffer_shp] # 3
        intersect_tr = [infra_trails, pip_buffer_shp] # 4
        intersect_rs = [rs2477_trails, pip_buffer_shp] # 5
        intersect_as = [infra_airstrips, pip_buffer_shp] # 6
        intersect_rw = [runways, pip_buffer_shp] # 7

        ## map document and dataframe
        mxd = arcpy.mapping.MapDocument("current")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]

        ## symbology layer files
        sourcePipSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/pip.lyr")
        sourceLoSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/lo.lyr") # 1
        sourceTrSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/tr.lyr") # 2
        sourcePpSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/pp.lyr") # 3
        sourceRdSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/rd.lyr") # 4
        sourceRsSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/rs.lyr") # 5
        sourceAsSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/as.lyr") # 6
        sourceRwSymbologyLayer = arcpy.mapping.Layer("E:/gina/poker/lyr/rw.lyr") # 7


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
        arcpy.Intersect_analysis(intersect_lo, pip_lo_in_buffer_shp, "ALL", "", "INPUT") # 1

        # Process: Intersect pip buffer with popn places
        arcpy.Intersect_analysis(intersect_pp, pip_popn_places_in_buffer_shp, "ALL", "", "INPUT") # 2

        # Process: Intersect pip buffer with road_centerlines
        arcpy.Intersect_analysis(intersect_rd, pip_roads_in_buffer_shp, "ALL", "", "INPUT") # 3

        # Process: Intersect pip buffer with rs2477 trails
        arcpy.Intersect_analysis(intersect_rs, pip_rs2477_in_buffer_shp, "ALL", "", "INPUT") # 4

        # Process: Intersect pip buffer with infra trails
        arcpy.Intersect_analysis(intersect_tr, pip_infra_trails_in_buffer_shp, "ALL", "", "INPUT") # 5

        # Process: Intersect pip buffer with infra airstrips
        arcpy.Intersect_analysis(intersect_as, pip_infra_airstrips_in_buffer_shp, "ALL", "", "INPUT") # 6

        # Process: Intersect pip buffer with runways
        arcpy.Intersect_analysis(intersect_rw, pip_runways_in_buffer_shp, "ALL", "", "INPUT") # 7

        # Process: Make feature layers and add to the map
        ## pip layer
        arcpy.MakeFeatureLayer_management(pip_point_3338, "Predicted Impact Point")
        addPipPointLayer = arcpy.mapping.Layer("Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, addPipPointLayer)

        ## pip land ownership layer
        arcpy.MakeFeatureLayer_management(pip_lo_in_buffer_shp, "Land Ownership within 3sigma of Predicted Impact Point") # 1
        add3sigmaLoLayer = arcpy.mapping.Layer("Land Ownership within 3sigma of Predicted Impact Point")
        arcpy.mapping.AddLayer(dataframe, add3sigmaLoLayer)

        ## pip populated places layer
        popn_places_records = int(arcpy.GetCount_management(pip_popn_places_in_buffer_shp).getOutput(0)) # 2
        if popn_places_records > 0:
            arcpy.MakeFeatureLayer_management(pip_popn_places_in_buffer_shp, "Populated Places within 3sigma of Predicted Impact Point")
            addPipPopnPlacesLayer = arcpy.mapping.Layer("Populated Places within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipPopnPlacesLayer)

        ## pip road centerlines layer
        rd_centers_records = int(arcpy.GetCount_management(pip_roads_in_buffer_shp).getOutput(0)) # 3
        if rd_centers_records > 0:
            arcpy.MakeFeatureLayer_management(pip_roads_in_buffer_shp, "Roads within 3sigma of Predicted Impact Point")
            addPipRoadsLayer = arcpy.mapping.Layer("Roads within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipRoadsLayer)

        ## pip rs2477 trails layer
        rs2477_records = int(arcpy.GetCount_management(pip_rs2477_in_buffer_shp).getOutput(0)) # 4
        if rs2477_records > 0:
            arcpy.MakeFeatureLayer_management(pip_rs2477_in_buffer_shp, "RS2477 Trails within 3sigma of Predicted Impact Point")
            addPiprR2477Layer = arcpy.mapping.Layer("RS2477 Trails within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipRoadsLayer)

        ## pip infra trails layer
        infra_trails_records = int(arcpy.GetCount_management(pip_infra_trails_in_buffer_shp).getOutput(0)) # 5
        if infra_trails_records > 0:
            arcpy.MakeFeatureLayer_management(pip_infra_trails_in_buffer_shp, "Other Trails within 3sigma of Predicted Impact Point")
            addPipOtherTrailsLayer = arcpy.mapping.Layer("Other Trails within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipOtherTrailsLayer)

        ## pip infra airstrips layer
        infra_airstrips_records = int(arcpy.GetCount_management(pip_infra_airstrips_in_buffer_shp).getOutput(0)) # 6
        if infra_airstrips_records > 0:
            arcpy.MakeFeatureLayer_management(pip_infra_airstrips_in_buffer_shp, "Airstrips within 3sigma of Predicted Impact Point")
            addPipAirstripsLayer = arcpy.mapping.Layer("Airstrips within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipAirstripsLayer)

        ## pip runways layer
        runways_records = int(arcpy.GetCount_management(pip_runways_in_buffer_shp).getOutput(0)) # 7
        if runways_records > 0:
            arcpy.MakeFeatureLayer_management(pip_runways_in_buffer_shp, "Runways within 3sigma of Predicted Impact Point")
            addPipRunwaysLayer = arcpy.mapping.Layer("Runways within 3sigma of Predicted Impact Point")
            arcpy.mapping.AddLayer(dataframe, addPipRunwaysLayer)

        # Add and calc Acres field for intersected Land Ownership
        arcpy.AddField_management(pip_lo_in_buffer_shp, "Acres", "DOUBLE")
        arcpy.CalculateField_management(pip_lo_in_buffer_shp, "Acres", "!shape.area@acres!", "PYTHON_9.3", "")

        # Summarize intersected Land Ownership by Owner and total Acres
        arcpy.Statistics_analysis(pip_lo_in_buffer_shp, pip_lo_in_buf_sum_dbf, "Acres SUM", "OWNER")
        # arcpy.MakeTableView_management(pip_lo_in_buf_sum_dbf)
        add3sigmaLoSumTbl = arcpy.mapping.TableView(pip_lo_in_buf_sum_dbf)
        arcpy.mapping.AddTableView(dataframe, add3sigmaLoSumTbl)

        # Symbolize and Refresh
        ## pip layer
        pip_layer = arcpy.mapping.ListLayers(mxd, "*Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, pip_layer, sourcePipSymbologyLayer, True)

        ## land ownership layer
        lo_layer = arcpy.mapping.ListLayers(mxd, "*Land Ownership within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, lo_layer, sourceLoSymbologyLayer, True)
        lo_layer.symbology.addAllValues()

        ## populated places layer
        pp_layer = arcpy.mapping.ListLayers(mxd, "*Populated Places within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, pp_layer, sourcePpSymbologyLayer, True)

        ## road layer
        rd_layer = arcpy.mapping.ListLayers(mxd, "*Roads within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, rd_layer, sourceRdSymbologyLayer, True)

        ## rs2477 layer -- Errored out saying that the index is out of range :(
        # rs_layer = arcpy.mapping.ListLayers(mxd, "*RS2477 Trails within 3sigma of Predicted Impact Point*", dataframe)[0]
        # arcpy.mapping.UpdateLayer(dataframe, rs_layer, sourceRsSymbologyLayer, True)

        ## trails layer
        tr_layer = arcpy.mapping.ListLayers(mxd, "*Other Trails within 3sigma of Predicted Impact Point*", dataframe)[0]
        arcpy.mapping.UpdateLayer(dataframe, tr_layer, sourceTrSymbologyLayer, True)

        ## airstrips layer -- Errored out saying that the index is out of range :(
        # as_layer = arcpy.mapping.ListLayers(mxd, "*Airstrips within 3sigma of Predicted Impact Point*", dataframe)[0]
        # arcpy.mapping.UpdateLayer(dataframe, as_layer, sourceAsSymbologyLayer, True)

        ## runways layer - commenting out to try to resolve the out of range errors :|
        # rw_layer = arcpy.mapping.ListLayers(mxd, "*Runways within 3sigma of Predicted Impact Point*", dataframe)[0]
        # arcpy.mapping.UpdateLayer(dataframe, rw_layer, sourceRwSymbologyLayer, True)

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

        return
