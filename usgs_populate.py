# Parse USGS JSON files
# Populates the sites using the original URL requests
# USGS site requires you to use a major filter (i.e. not dump everything)
#
# Creates a gaugesall.json file which is then used to populate the MongoDB
# database using mongoimport.
#
# This version creates a customized dump because MongoDB apparently doesn't like
# the JSON from the standard Python functions
#
# Copyright Gordon Haff 2013
# Released under MIT License http://opensource.org/licenses/MIT

import json
import string
import sys
import io
import urllib2

output = {}

# Lookup table for the state codes returned by USGS (ANSI codes) to 2 letter abbreviations
# The two letter abbreviations are needed to construct the URL for the individual gauge pages

statelookup = {
"01" : "al",
"02" : "ak",
"04" : "az",
"05" : "ar",
"06" : "ca",
"08" : "co",
"09" : "ct",
"10" : "de",
"11" : "dc",
"12" : "fl",
"13" : "ga",
"15" : "hi",
"16" : "id",
"17" : "il",
"18" : "in",
"19" : "ia",
"20" : "ks",
"21" : "ky",
"22" : "la",
"23" : "me",
"24" : "md",
"25" : "ma",
"26" : "mi",
"27" : "mn",
"28" : "ms",
"29" : "mo",
"30" : "mt",
"31" : "ne",
"32" : "nv",
"33" : "nh",
"34" : "nj",
"35" : "nm",
"36" : "ny",
"37" : "nc",
"38" : "nd",
"39" : "oh",
"40" : "ok",
"41" : "or",
"42" : "pa",
"44" : "ri",
"45" : "sc",
"46" : "sd",
"47" : "tn",
"48" : "tx",
"49" : "ut",
"50" : "vt",
"51" : "va",
"53" : "wa",
"54" : "wv",
"55" : "wi",
"56" : "wy",
"60" : "as",
"66" : "gu",
"69" : "mp",
"72" : "pr",
"74" : "um",
"78" : "vi"
}

fileout = open('gaugesall.json', 'w')


# USGS requires a major filter. I'm using huc (hydrological area)
# Range from 01 to 21

for i in range(1,22):
    
    if i < 10:
        hucstring = "0" + str(i)
    else:
        hucstring = str(i)
        
    requesturl = "http://waterservices.usgs.gov/nwis/iv/?format=json,1.1&huc="+ hucstring + "&parameterCd=00060,00065&siteType=ST"

    req = urllib2.Request(requesturl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    entry = json.loads(f.read())
    
    print "loaded"

# for now we're working with new England data from file
# usgsfile = open('usgsnewengland2.json')
# load the json file


# load the JSON. (loads doesn't work in this case)
# entry = json.load(usgsfile)
# count the number of locations

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
        asitename =  entry['value']['timeSeries'][count]['sourceInfo']['siteName']
    
#Lat
        alat = entry['value']['timeSeries'][count]['sourceInfo']['geoLocation']['geogLocation']['latitude']

#Long
        along = entry['value']['timeSeries'][count]['sourceInfo']['geoLocation']['geogLocation']['longitude']
        
        astatecode = entry['value']['timeSeries'][count]['sourceInfo']['siteProperty'][2]['value']

# save the variable code
#    variablecode = str(entry['value']['timeSeries'][count]['variable']['variableCode'][0]['variableID'])

# save the variable value

#    variablevalue = str(entry['value']['timeSeries'][count]['values'][0]['value'][0]['value'])

#Gage ht. ft. variableID 45807202

#    if variablecode == '45807202':
#        print variablevalue + " ft"

#Discharge cfs variableID 45807197

#    if variablecode == '45807197':
#         print variablevalue + " cfs"
         
    #save creation time so that we can throw out any stale data
    
#    creationtime = entry['value']['queryInfo']['creationTime']

# For the initial population, we just fill in zeros for the flow/height/creation time
# lat/long is setup this way because that's hoe MongoDB likes it
    
        agauge = {
            
            "sitename": asitename,
            "pos": [along, alat],
            "flow": 0,
            "height": 0,
            "timestamp": 0,
            "statecode": statelookup[astatecode]
            
            
        }
        

        output[agaugenum] = agauge
                
    
        count = count - 1
        
for k in output:
    
    agaugestr = '{ "_id" : "' + k + '",'
    asitenamestr = ' "sitename" : "' + output[k]["sitename"] + '" ,'
    astatecodestr = ' "statecode" : "' + output[k]["statecode"] + '" ,'
    aposstr = ' "pos" : [' + str(output[k]["pos"][0]) + ', ' + str(output[k]["pos"][1]) + '] ,'
    aflowstr = ' "flow" : "' + str(output[k]["flow"]) + '" ,'
    aheightstr = ' "height" : "' + str(output[k]["height"]) + '" ,'
    atimestampstr = ' "timestamp" : "' + str(output[k]["timestamp"]) + '" }' 

    outstr= agaugestr + asitenamestr + astatecodestr + aposstr  + aflowstr + aheightstr + atimestampstr

    print outstr
    
# do the final dump to a JSON-ish file
# MongoDB is sort of picky

    fileout.write(outstr)
    fileout.write("\n")
    
fileout.close()




