openshift-mongo-flask-example
=============================

This is the code to go along with the [OpenShift blog piece](https://openshift.redhat.com/community/blogs/rest-web-services-with-python-mongodb-and-spatial-data-in-the-cloud) on how to use Flask (python) with MongoDB to create a REST like web service with spatial data

Running on OpenShift
----------------------------

Create an account at http://openshift.redhat.com/

Create a python-2.6 application and add a MongoDB cartridge to the app

    rhc app create -a pythonws -t python-2.6
    rhc app cartridge add -a pythonws -c mongodb-2.2

Add this upstream flask repo


    cd pythonws
    git remote add upstream -m master git://github.com/openshift/openshift-mongo-flask-example.git
    git pull -s recursive -X theirs upstream master
    
Then push the repo upstream

    git push
    
To add the data to the MongoDB instance please follow the instructions on this blog:
[Mongo Spatial on OpenShift](https://openshift.redhat.com/community/blogs/spatial-mongodb-in-openshift-be-the-next-foursquare-part-1)

Now, ssh into the application.

Add the data to a collection called parkpoints:

    mongoimport -d pythonws -c parkpoints --type json --file $OPENSHIFT_REPO_DIR/parkcoord.json  -h $OPENSHIFT_MONGODB_DB_HOST  -u admin -p $OPENSHIFT_MONGODB_DB_PASSWORD

    
Create the spatial index on the documents:

    mongo
    use pythonws
    db.parkpoints.ensureIndex( { pos : "2d" } );

Once the data is imported you can now checkout your application at:

    http://pythonws-$yournamespace.rhcloud.com/ws/parks
    
