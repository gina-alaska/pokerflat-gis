# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# buff_nautical_miles.py
# Created on: 2017-12-01 15:21:46.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
Predicted_Impact_Point = "Predicted Impact Point"
pip_point_3338_Buffer_NMunits = "C:\\Users\\Pete\\Documents\\ArcGIS\\Default.gdb\\pip_point_3338_Buffer_NMunits"

# Process: Buffer
arcpy.Buffer_analysis(Predicted_Impact_Point, pip_point_3338_Buffer_NMunits, "20 NauticalMiles", "FULL", "ROUND", "NONE", "", "PLANAR")

