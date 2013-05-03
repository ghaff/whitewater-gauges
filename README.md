openshift-mongo-flask-example
=============================

This is the code to go along with the [OpenShift blog piece](https://openshift.redhat.com/community/blogs/rest-web-services-with-python-mongodb-and-spatial-data-in-the-cloud) on how to use Flask (python) with MongoDB to create a REST like web service with spatial data
**Please note that this only works with Python-2.6 cartridge**

Running on OpenShift
----------------------------

Create an account at http://openshift.redhat.com/

Create a python-2.6 application and add a MongoDB cartridge to the app

    rhc app create pythonws python-2.6 mongodb-2.2 --from-code git://github.com/openshift/openshift-mongo-flask-example.git
    
To add the data to the MongoDB instance please follow the instructions on this blog:
[Mongo Spatial on OpenShift](https://openshift.redhat.com/community/blogs/spatial-mongodb-in-openshift-be-the-next-foursquare-part-1)

Now, ssh into the application.

Add the data to a collection called parkpoints:

    mongoimport -d pythonws -c parkpoints --type json --file $OPENSHIFT_REPO_DIR/parkcoord.json  -h $OPENSHIFT_MONGODB_DB_HOST  -u admin -p $OPENSHIFT_MONGODB_DB_PASSWORD --port $OPENSHIFT_MONGODB_DB_PORT

    
Create the spatial index on the documents:

    mongo
    use pythonws
    db.parkpoints.ensureIndex( { pos : "2d" } );

Once the data is imported you can now checkout your application at:

    http://pythonws-$yournamespace.rhcloud.com/ws/parks
 
License
-------

This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to CC0 (http://creativecommons.org/publicdomain/zero/1.0/)
