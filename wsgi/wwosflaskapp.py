import os
import io
import sys
import string
from flask import Flask
from flask import request
from flask import render_template
import pymongo
import json
from bson import json_util
from bson import objectid
import re
import urllib2
from time import time
from time import sleep

# Note order of coordinates is long/lat


app = Flask(__name__)
#add this so that flask doesn't swallow error messages
app.config['PROPAGATE_EXCEPTIONS'] = True

#a base urls that returns all the gauges in the collection (of course in the future we would implement paging)
@app.route("/ws/gauges")
def gauges():
    #setup the connection to the gauges database
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges

    #query the DB for all the gaugepoints
    result = db.gaugepoints.find()

    #Now turn the results into valid JSON
    return str(json.dumps({'results':list(result)},default=json_util.default))



#find gauges within a lot/long bounding box passed in as query parameters (within?lat1=45.5&&lon1=-82&lat2=42&lon2=-84)
@app.route("/ws/gauges/within")
def within():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges

    #get the request parameters
    lat1 = float(request.args.get('lat1'))
    lon1 = float(request.args.get('lon1'))
    lat2 = float(request.args.get('lat2'))
    lon2 = float(request.args.get('lon2'))

    #use the request parameters in the query
    result = db.gaugepoints.find({"pos": {"$within": {"$box" : [[lon1,lat1],[lon2,lat2]]}}})

    #turn the results into valid JSON
    return str(json.dumps(list(result),default=json_util.default))

# for manual updates
@app.route("/ws/gauges/update")
def update():

    statelist = ["al","ak","az","ar","ca","co","ct","de","dc","fl","ga","hi","id","il","in","ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj","nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy","pr"]
    
    #setup the connection to the gauges database
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges
        
        
    # USGS requires a major filter. I'm using state name
    # Note that some filters seem to produce JSON rsponses that are too large to process
    
    for i in statelist:
        
        try:
    
            requesturl = "http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&stateCd=" + i +"&parameterCd=00060,00065&siteType=ST"
    
    
            #code
            req = urllib2.Request(requesturl)
            opener = urllib2.build_opener()
            f = opener.open(req)
           
            entry = json.loads(f.read())
        
        except:
            continue
        
    
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
            try:
                variablevalue = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['value'])
            except:
                variablevalue = ""
    
    # save the time stamp
    
            try:
                creationtime  = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['dateTime'])
            except:
                creationtime = ""
    
    #Gage ht. ft. variableID 45807202
    
            if variablecode == '45807202':
                db.gaugepoints.update({"_id":agaugenum},{"$set":{"height":variablevalue}})
    
    
    #Discharge cfs variableID 45807197
    
            if variablecode == '45807197':
                db.gaugepoints.update({"_id":agaugenum},{"$set":{"flow":variablevalue}})
         
    #save creation time so that we can throw out any stale data
    
            db.gaugepoints.update({"_id":agaugenum},{"$set":{"timestamp":creationtime}})
    
            count = count - 1
            
        sleep(30)

            
    return "Update completed. "

# for manual updates
@app.route("/ws/gauges/update/state")
def updatestate():

    statelist = ["al","ak","az","ar","ca","co","ct","de","dc","fl","ga","hi","id","il","in","ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj","nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy","pr"]
    
    #setup the connection to the gauges database
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges

        
    i = request.args.get('st')
        
        


    requesturl = "http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&stateCd=" + i +"&parameterCd=00060,00065&siteType=ST"


        #code
    req = urllib2.Request(requesturl)
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
#same across entries.

# save the variable code
        variablecode = str(entry['value']['timeSeries'][count]['variable']['variableCode'][0]['variableID'])

# save the variable value
        try:
            variablevalue = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['value'])
        except:
            variablevalue = ""

# save the time stamp

        try:
            creationtime  = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['dateTime'])
        except:
            creationtime = ""

#Gage ht. ft. variableID 45807202

        if variablecode == '45807202':
            db.gaugepoints.update({"_id":agaugenum},{"$set":{"height":variablevalue}})


#Discharge cfs variableID 45807197

        if variablecode == '45807197':
            db.gaugepoints.update({"_id":agaugenum},{"$set":{"flow":variablevalue}})
     
#save creation time so that we can throw out any stale data

        db.gaugepoints.update({"_id":agaugenum},{"$set":{"timestamp":creationtime}})

        count = count - 1
        
    updatemsg = "Update completed for state " + i + "\n"
    
    conn.close()

            
    return updatemsg
            


@app.route("/")
def test():
    return render_template("index.html")
    
#need this in a scalable app so that HAProxy thinks the app is up
@app.route("/test")
def blah():
    return "hello world"

if __name__ == "__main__":
    app.run()

