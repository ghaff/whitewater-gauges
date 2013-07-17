import os
from flask import Flask
from flask import request
from flask import render_template
import pymongo
import json
from bson import json_util
from bson import objectid
import re

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



#find gauges near a lat and long passed in as query parameters (near?lat=45.5&lon=-82)
@app.route("/ws/gauges/near")
def near():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #use the request parameters in the query
    result = db.gaugepoints.find({"pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))

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
    return str(json.dumps({'results' : list(result)},default=json_util.default))




#find gauges with a certain name (use regex) near a lat long pair such as above
@app.route("/ws/gauges/name/near/<name>")
def nameNear(name):
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn.gauges

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #compile the regex we want to search for and make it case insensitive
    myregex = re.compile(name, re.I)

    #use the request parameters in the query along with the regex
    result = db.gaugepoints.find({"Name" : myregex, "pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps(list(result),default=json_util.default))


@app.route("/")
def test():
    return render_template("index.html")
    
#need this in a scalable app so that HAProxy thinks the app is up
@app.route("/test")
def blah():
    return "hello world"

if __name__ == "__main__":
    app.run()

