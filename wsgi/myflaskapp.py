import os
from flask import Flask
from flask import request
import pymongo
import json
from bson import json_util
from bson import objectid
import re

app = Flask(__name__)
#add this so that flask doesn't swallow error messages
app.config['PROPAGATE_EXCEPTIONS'] = True

#a base urls that returns all the parks in the collection (of course in the future we would implement paging)
@app.route("/ws/parks")
def parks():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #query the DB for all the parkpoints
    result = db.parkpoints.find()

    #Now turn the results into valid JSON
    return str(json.dumps({'results':list(result)},default=json_util.default))


#return a specific park given it's mongo _id
@app.route("/ws/parks/park/<parkId>")
def onePark(parkId):
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #query based on the objectid
    result = db.parkpoints.find({'_id': objectid.ObjectId(parkId)})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


#find parks near a lat and long passed in as query parameters (near?lat=45.5&lon=-82)
@app.route("/ws/parks/near")
def near():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #use the request parameters in the query
    result = db.parkpoints.find({"pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


#find parks with a certain name (use regex) near a lat long pair such as above
@app.route("/ws/parks/name/near/<name>")
def nameNear(name):
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #compile the regex we want to search for and make it case insensitive
    myregex = re.compile(name, re.I)

    #use the request parameters in the query along with the regex
    result = db.parkpoints.find({"Name" : myregex, "pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


@app.route("/test")
def test():
    return "<strong>It actually worked</strong>"
    
#need this in a scalable app so that HAProxy thinks the app is up
@app.route("/")
def blah():
    return "hello world"

if __name__ == "__main__":
    app.run()

