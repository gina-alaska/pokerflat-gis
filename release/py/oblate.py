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

import math

def sp_azi(latit_sp,longit_sp,distance,azi):
    #Math will be done here to calculate the ending point from the parameters provided
    #I will more then likely print from the function rather

    #Calculates Angular Distance
    ang_distance = distance/6371

    #Calculate the ending point latitude
    p1 = math.sin(latit_sp)*math.cos(ang_distance)
    p2 = math.cos(latit_sp)*math.sin(ang_distance)*math.cos(azi)
    lat_ep = math.asin(p1+p2)

    #Calculate the ending point longitude
    p3 = math.sin(azi)*math.sin(ang_distance)*math.cos(latit_sp)
    p4 = math.cos(ang_distance) - (math.sin(latit_sp)*math.sin(lat_ep))
    long_ep = longit_sp + math.atan2(p3,p4)

    #This will figure out whether the user wants DMS or DD back
    DMSorDD = raw_input("Would you like your result in Degrees-Minutes-Seconds (DMS) or Decimal Degrees (DD)?")
    if DMSorDD == "DMS":
        convert_DDtoDMS(lat_ep)
        convert_DDtoDMS(long_ep)
    else:
        print "Final Point: Latitude: " + lat_ep + " Decimal Degrees"
        print long_ep + " Decimal Degrees"


def range_azimuth(latit_sp,longit_sp,latit_ep,longit_ep):
    #Math will be done here to calculate the azimuth from the parameters provided

    delta_lat = math.fabs(latit_ep-latit_sp)
    delta_long = math.fabs(longit_ep-longit_sp)
    #Math used to calculate the distance between two points
    a = (math.sin(delta_lat/2)**2) + math.cos(latit_sp)*math.cos(latit_ep)*(math.sin(delta_long/2)**2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    distance = 6371*c

    #Math used to calculate the azimuth between two points
    p1 = math.sin(delta_long)*math.cos(latit_ep)
    p2 = math.cos(latit_sp)*math.sin(latit_ep)
    p3 = math.sin(latit_sp)*math.cos(latit_ep)*math.cos(delta_long)
    azimuth = math.atan2(p1,p2-p3)

    #Returns the distance in kilometers and azimuth in radians
    print "This is your Range in Kilometers: " + distance
    print "This is your azimuth in degrees: " + azimuth


def convert_DMStoDD(deg,minute,sec):
    #Math to convert DMS to DD to make other calculations easier
    result = 0
    result = sec/60.
    result = result + minute
    result = result/60.
    if deg >= 0:
        result = result+deg
    else:
        result = deg-result

    return result

def convert_DDtoDMS(dec_deg):
    degree = int(dec_deg)

    if dec_deg >= 0:
        r1 = dec_deg - degree
        r1 = r1*60
        minutes = int(r1)
        seconds = (r1-minutes)*60

        print degree + "degrees " + minutes + "minutes " + seconds + "seconds"
    else:
        r1 = math.fabs(dec_deg+degree)
        r1 = r1*60
        minutes = int(r1)
        seconds = (r1-minutes)*60

        print degree + "degrees " + minutes + "minutes " + seconds + "seconds"


#Asks the user for whether they want to enter a DMS or DD value for the beginning latitude and longitude
DMS_DD = raw_input("Do you have a latitude and longitude in Degrees-Minutes-Seconds (DMS) or Decimal Degrees (DD)?")

if DMS_DD == "DMS":
    #Asks the user for the degrees, minutes and seconds for latitude
    lat_degree = float(raw_input("What is your latitude degree value?"))
    lat_minutes = float(raw_input("What is your latitude minutes value?"))
    lat_seconds = float(raw_input("What is your latitude seconds value?"))

    #Asks the user for the degrees, minutes and seconds for longitude
    long_degree = float(raw_input("What is your longitude degree value?"))
    long_minutes = float(raw_input("What is your longitude minutes value?"))
    long_seconds = float(raw_input("What is your longitude seconds value?"))

    latit_sp = convert_DMStoDD(lat_degree,lat_minutes,lat_seconds)
    longit_sp = convert_DMStoDD(long_degree,long_minutes,long_seconds)

else:
    #Asks the user for the Decimal Degrees value for latitude and longitude
    latit_sp = float(raw_input("What is your starting latitude?"))
    longit_sp = float(raw_input("What is your starting longitude"))

#Asks the user for the bearing or azimuth off of true north
azi = raw_input("What is your starting azimuth? *If none, press enter*")
#Asks the user for the distance or range
distance = raw_input("What is your distance? *If none, press enter and please enter it in km units*")
#Asks for the user for the ending latitude and longitude, if needed.
EP = raw_input("Do you have an ending point to enter?")

if EP == "Yes":
    DMS_DD_EP = raw_input("Do you have a latitude and longitude in Degrees-Minutes-Seconds (DMS) ot Decimal Degrees (DD)?")
    if DMS_DD == "DMS":
        #Asks the user for the degrees, minutes and seconds for latitude
        lat_degree = float(raw_input("What is your latitude degree value?"))
        lat_minutes = float(raw_input("What is your latitude minutes value?"))
        lat_seconds = float(raw_input("What is your latitude seconds value?"))

        #Asks the user for the degrees, minutes and seconds for longitude
        long_degree = float(raw_input("What is your longitude degree value?"))
        long_minutes = float(raw_input("What is your longitude minutes value?"))
        long_seconds = float(raw_input("What is your longitude seconds value?"))

        latit_ep = convert_DMStoDD(lat_degree,lat_minutes,lat_seconds)
        longit_ep = convert_DMStoDD(long_degree,long_minutes,long_seconds)
    else:
        #Asks the user for the Decimal Degrees value for latitude and longitude
        latit_ep = raw_input("What is your ending latitude? *If none, press enter*")
        longit_ep = raw_input("What is your ending longitude? *If none, press enter*")


if latit_sp!="" and longit_sp!="":
    if distance!="" and azi!="":
        sp_azi(latit_sp,longit_sp,distance,azi)

    elif latit_ep!="" and longit_ep!="":
        range_azimuth(latit_sp,longit_sp,latit_ep,longit_ep)

    else:
        print "You did not provide enough data."


else:
    print "You did not provide enough data."


