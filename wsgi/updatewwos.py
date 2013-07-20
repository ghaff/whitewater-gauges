#!/usr/bin/env python

import os
import io
import sys
import string
import pymongo
import json
from bson import json_util
from bson import objectid
import re
import urllib2
from time import time
from time import sleep

#setup the connection to the gauges database
conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
db = conn.gauges
    
    
# USGS requires a major filter. I'm using huc (hydrological area)
# Range from 01 to 21

#This does not seem to complete reliably

for i in range(1,2):

    if i < 10:
        hucstring = "0" + str(i)
    else:
        hucstring = str(i)
        
    


    
#    requesturl = "http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&huc="+ hucstring + "&parameterCd=00060,00065&siteType=ST"

    requestURL = "http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&stateCd=ny&parameterCd=00060,00065&siteType=ST"

    print "Loading request"


        #code
    req = urllib2.Request(requesturl)
    opener = urllib2.build_opener()
    f = opener.open(req)

    
    entry = json.loads(f.read())
    
    print "Loaded request "


    count = int (len(entry['value']['timeSeries']) - 1)

    while count >= 0:
#We construct an array of the relevant values associated with a guage number
#Note that gage height and discharge are in separate entries
#Right here we're just filling out the "permanent" values


#Gauge Number. This will be the dictionary index
        agaugenum = entry['value']['timeSeries'][count]['sourceInfo']['siteCode'][0]['value']

#Site Name
#Going to assume that all the "permanent" attributes of a guage number are the
#same across entries.

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

        
#        sleep(30)
        
print "All completed!"
   
    


