#!/usr/bin/env python

# Parse USGS JSON files
# Populates the sites using the original URL requests
# USGS site doesn't seem to let you just dump everything
# For this purpose we use the hydrological are
# This value goes from 01 to 21 and makes it easy to construct a series of operations

# This version creates a customized dump because MongoDB apparently doesn't like
# a literal JSON format.
# Gordon Haff

import json
import string
import sys
import io
import urllib2
import pymongo
import os

output = {}

#setup the connection to the gauges database
conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
db = conn.gauges

# for working purposes, only pulling in New England

for i in range(0,1):

    req = urllib2.Request("http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&huc=01&parameterCd=00060,00065&siteType=ST")
    opener = urllib2.build_opener()
    f = opener.open(req)
    entry = json.loads(f.read())
    

    count = int (len(entry['value']['timeSeries']) - 1)

    while count >= 0:
#We construct an array of the relevant values associated with a guage number
#Note that gage height and discharge are in separate entries
#Right here we're just filling out the "permanent" values


#Gauge Number. This will be the dictionary index
        agaugenum = entry['value']['timeSeries'][count]['sourceInfo']['siteCode'][0]['value']

#Site Name
#Going to assume that all the "permanent" attributes of a guage number are the
#same across entries. We'll use the first instance in any case
#        asitename =  entry['value']['timeSeries'][count]['sourceInfo']['siteName']
    
#Lat
#        alat = entry['value']['timeSeries'][count]['sourceInfo']['geoLocation']['geogLocation']['latitude']

#Long
#        along = entry['value']['timeSeries'][count]['sourceInfo']['geoLocation']['geogLocation']['longitude']

# save the variable code
        variablecode = str(entry['value']['timeSeries'][count]['variable']['variableCode'][0]['variableID'])

# save the variable value

        variablevalue = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['value'])

# save the time stamp

        creationtime  = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['dateTime'])

#Gage ht. ft. variableID 45807202

        if variablecode == '45807202':
            db.gaugepoints.update({"_id":agaugenum},{"$set":{"height":variablevalue}})


#Discharge cfs variableID 45807197

        if variablecode == '45807197':
            db.gaugepoints.update({"_id":agaugenum},{"$set":{"flow":variablevalue}})
         
#save creation time so that we can throw out any stale data
    

        db.gaugepoints.update({"_id":agaugenum},{"$set":{"timestamp":creationtime}})
        

        
                
    
        count = count - 1
        





