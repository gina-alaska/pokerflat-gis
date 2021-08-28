pip_dir = "E:/gina/poker/pip"
arcpy.env.workspace = pip_dir
shp_list = arcpy.ListFeatureClasses()
mxd = arcpy.mapping.MapDocument("current")
dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
for shp in shp_list:
    layername = shp[:-4]
    if not str(layername) == "pip_buffer":
        arcpy.MakeFeatureLayer_management(shp, layername)

layerList = arcpy.mapping.ListLayers(mxd)
layer = layerList[1]
# arcpy.mapping.UpdateLayer(dataframe, layer, layerList[3], True)
# layer.symbology.addAllValues()
layer.visible = True
layerList[0].visible = True
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

ext = layer.getExtent()
dataframe.extent = ext




