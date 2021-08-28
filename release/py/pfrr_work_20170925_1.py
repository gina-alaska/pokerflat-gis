# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# pfrr_work_20170925_1.py
# Created on: 2017-09-25 09:13:46.00000
#   (generated by ArcGIS/ModelBuilder)
# Description:
# Generates the C:\pfrr_work\ directory.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
from arcpy import env
import csv
import os
import sys

# Local variables:
Folder_Location = "C:\\"
Lon = sys.argv[1]
Lat = sys.argv[2]
# pfrr_work = Folder_Location
# pfrr_predicted_impact_xy_dbf = "C:\\pfrr_work\\pfrr_predicted_impact_xy.dbf"
# Output_PIP_Tbl_Lon = pfrr_predicted_impact_xy_dbf
# PIP_Tbl_Lat_Lon = Output_PIP_Tbl_Lon
# pfrr_work = arcpy.env.workspace

# Process: ArcPy Create Folder
# arcpy.CreateFolder_management(Folder_Location, "pfrr_work")

# Process: OS Makedirs
newpath = "C:/pfrr_work"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# Set Geoprocessing environments
arcpy.env.scratchWorkspace = 'C:/pfrr_work'
arcpy.env.workspace = 'C:/pfrr_work'

print arcpy.env.workspace

# Generate pip_table.csv in pfrr_work/
with open('C:/pfrr_work/pip_table.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['ID', 'Lon', 'Lat'])
    filewriter.writerow(['1', Lon, Lat])
#    filewriter.writerow(['Steve', 'Software Developer'])
#    filewriter.writerow(['Paul', 'Manager'])

# Process: Create Table
# arcpy.CreateTable_management(pfrr_work, "pfrr_predicted_impact_xy.dbf", "", "")

# Process: Add Lon Field
# arcpy.AddField_management(pfrr_predicted_impact_xy_dbf, "Lon", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Add Lat Field
# arcpy.AddField_management(Output_PIP_Tbl_Lon, "Lat", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
