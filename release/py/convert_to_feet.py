#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Patrick
#
# Created:     23/03/2018
# Copyright:   (c) Patrick 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import math
import os
import sys
import tempfile

from arcpy import env

def toFeet(value):
    num = float(value)*3280.84
    value = str(num)
    return value



val = 10
print val