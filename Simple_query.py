# Andy Dean

# andy.dean@preservica.com      13/02/2020

# Run API search using a simple search term
#
# For use with Preservica version 6.x
# 
# THIS SCRIPTS IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
# Use at your own risk. If it works for you share it, and please provide feedback or share improvements at developers.preservica.com (going live May 2020)
#
# Requires Python3.x (i.e. 3.6). Use PIP3 to install "pymsgbox".


#################################################################################################
##################################        Import       ##########################################
#################################################################################################

from datetime import datetime

import json

import requests

import xml.etree.ElementTree as ET

import pymsgbox

from preservicatoken import securitytoken

import configparser

#################################################################################################
##################################     Declarations    ##########################################
#################################################################################################

pageinc = int
varpages = int
pagestart= int
pagemax = int


#################################################################################################
#################################    Security Token    ##########################################
#################################################################################################

def gettoken(config_input):

    accesstoken = securitytoken(config_input)
    
    return accesstoken


#################################################################################################
################################     JSON Query Routine   #######################################
#################################################################################################

def JSON_search_query(temptoken, wftrackingfile, wfoutputfile, hostval, query_string, pageinc, hitcheck):

    wftrack = open(wftrackingfile, "w")
    wfresult = open(wfoutputfile, "w")

    wftrack.write(query_time + " : search term " + query_string + "\r")
    wfresult.write(query_time + " : search term " + query_string + "\r")
    
    headers = {
    'Preservica-Access-Token': temptoken,
    'Content-Type': 'application/x-www-form-urlencoded',
    'cache-control': "no-cache"
    }

    #first iteration
    url = "https://" + hostval + "/api/content/search"
        
    json_data = '{"q": "' + query_string + '"}'
    parsed_json = (json.loads(json_data))
    
    payload = 'start=0&max=1&metadata=xip&q=' + json_data
    simple_response = requests.request("POST", url, data=payload, headers=headers)
    
    parsed_json_response = json.loads(simple_response.text)

    vartotalHits = int((parsed_json_response['value'])['totalHits'])
    
    startval  = 0
    counter = 0
    while startval < (vartotalHits):
        if hitcheck == 'true':
            startval = vartotalHits + 1

        print("_________________________________________________________________________________________")
              
        payload = 'start=' + str(startval) +  '&max=' + str(pageinc) + '&metadata=xip&q=' + json_data
   
        simple_response = requests.request("POST", url, data=payload, headers=headers)
        parsed_json_response = json.loads(simple_response.text)
        print(parsed_json_response)
        strSOIO = ((parsed_json_response['value'])['objectIds'])
        for SOIOloop in strSOIO:
            wfresult.write(str(counter) + " " + str(startval) + " " + str(pageinc) + " " + SOIOloop)
            wfresult.write("\r")
            counter = counter + 1
        startval = startval + pageinc

    wfresult.close()
    wftrack.close()
    return vartotalHits
   

#################################################################################################
##################################            MAIN           ####################################
#################################################################################################


# output files
query_time = datetime.now().strftime("%Y-%m-%d_%I-%M-%S")
wftrackingfile = "query_tracker_" + query_time + ".txt"
wfoutputfile = "query_" + query_time + ".txt"

#interactive
config_file = pymsgbox.confirm(text='Select the system to query', title='Simple Search Routine', buttons=['beta', 'preview','config'])
query_string = pymsgbox.prompt(text='Your search query is:', title='Simple Search Routine')

# config file
config_input = config_file + ".ini"
config = configparser.ConfigParser()
config.sections()
config.read(config_input)
hostval = config['DEFAULT']['Host']
hostversion = config['DEFAULT']['Version']

# results per page
pageinc = 5
hitcheck = 'true'

# get a security token
temptoken = gettoken(config_input)

# run search

totalHits = JSON_search_query(temptoken, wftrackingfile, wfoutputfile, hostval, query_string, pageinc, hitcheck)
msg = 'The total number of hits for this query is' + str(totalHits) + ': Click OK to continue '
hits_continue = pymsgbox.confirm(text = msg, title='Simple Searach Query', buttons=['OK', 'Cancel'])

if hits_continue == "Cancel":
    print("Cancel")
elif hits_continue == "OK":
    print("We'll continue")
    hitcheck = 'false'
    totalHits = JSON_search_query(temptoken, wftrackingfile, wfoutputfile, hostval, query_string, pageinc, hitcheck)
    

