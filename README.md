# Project Description
Poker Flat Research Rocket Range GIS, Data Management and Decision Support

Poker Flat Research Rocket Range has asked GINA to build an interactive GIS (optionally web-based)
for plotting “predicted impact point” (based on WGS84 Lat/Lon in decimal degrees) surrounded by a
3σ circle representing the area within which the rocket will impact at the 90% confidence interval,
then intersecting the 3σ circle with an underlying populated places layer, land ownership
(e.g. native allotments), culturally significant sites, winter use areas (wood cutting, traplines etc)
and winter trails.  Data resulting from this intersection analysis will be used to generate a report
detailing those features that are contained by the 3σ circle which will help make the decision
to launch or not to launch.

This repo will be used to stage GIS data, project files, source code for custom tools, and
documentation.  

# Build notes
- Current build is in ArcGIS Desktop version 10.6.  You must have ArcGIS Desktop to use the PFRR toolbox (ArcGIS Pro version is planned).
- To install, download and unpackage (unzip) the directory structure found in file gina.zip onto directly to the `C:\` drive on a Windows PC
  - https://github.com/gina-alaska/pokerflat-gis/blob/master/release/
- The current release project file is located in C:\gina\poker\mxd\<filename>.mxd
- After the project file has been loaded into ArcMap, locate the PFRR Tools toolbox in the ArcToolbox window.
  - Note: if the PFRR Tools toolbox is not located in the ArcToolbox window, right-click and add the file from the directory below to your ArcToolbox window: 
    - C:\gina\poker\py\py_c\PFRRranger...<release version>.pyt
- The PFRR Tools toolbox contains four tools as follows:
  1.  PFRR Pre-launch
  2.  Bearing and Range
  3.  Ending Point
  4.  Convert Units
  
# PFRR Pre-launch tool notes
- The PFRR Pre-launch tool requires the following parameters to run:
  1.  Mission name
  2.  Longitude and Latitude of the nominal impact point
  3.  Radius of the 3σ circle in nautical miles
- Output from the PFRR Pre-launch tool is listed below:
  1.  The location of the nominal impact point
  2.  The circle polygon of the 3σ circle and 2 subordinate range rings
  3.  The output from intersecting the land ownership layer with the 3σ circle polygon
  4.  The output from intersecting the Poker Flat Populated Places layer with with the 3σ circle
  5.  The output from intersecting the Alaska Fire Service (AFS) Known Sites layer with the 3σ circle
- Output feature classes will be stored in a file geodatabase located in C:\gina\poker\gdb\ named <Mission Name>.gdb
  
#  Contact information
For questions about these data or this project, please contact 
```
John Pace - DirectorGeographic Information Network of Alaska
University of Alaska Fairbanks - Geophysical Institute
2156 North Koyukuk Drive - Elvey 201
Fairbanks, AK  99775
(907) 474-6897
jpace6@alaska.edu
```
or
```
Peter Hickman - GIS Project Manager
Geographic Information Network of Alaska
University of Alaska Fairbanks - Geophysical Institute
2156 North Koyukuk Drive - Elvey 201
Fairbanks, AK  99775
(907) 474-1567
pjhickman@alaska.edu
```
