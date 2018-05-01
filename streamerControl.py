########################
# Libraries
########################

import os
import string
# import paho.mqtt.client as mqtt
from Adafruit_IO import *
import time
import threading
import requests
import sys

import subprocess

########################
# Globals
########################
PLACE = ""
ADAFRUIT_IO_USERNAME = "giy"        # Adafruit.IO user ID
ADAFRUIT_IO_KEY = "c0ee9df947d4443286872f667e389f1f"    # Adafruit.IO user key
STREAM_BASE_URL = "http://weatherreport.kr:8000/"
STREAM_CHECK_POINT = "http://weatherreport.kr:8000/status-json.xsl"
ON_VALUE = "1"
OFF_VALUE = "0"

SCRIPT_PATH = "/home/pi/bin/solarRPI/"

cur_r = 0
prv_r = 0


########################
# Functions
########################

def topic_str(x):
    return {
        "IMSI" : "text_console",
        "SONGDO" : "text_console",
        "XX" : "text_console",
        "DEFAULT" : "text_console"
    }.get(x) 
    
def topic_play(x):
    return {
        "IMSI" : "text_console",
        "SONGDO" : "text_console",
        "XX" : "text_console",
        "DEFAULT" : "text_console"
    }.get(x) 

def feed_recVol(x):
    return {
        "IMSI" : "rec_vol_0",
        "SONGDO" : "rec_vol_1",
        "XX" : "rec_vol_2",
        "DEFAULT" : "rec_vol_0"
    }.get(x) 

def mp(x):
    return {
        "IMSI" : "xx.mp3",
        "SONGDO" : "imsi.mp3",
        "XX" : "songdo.mp3",
        "DEFAULT" : "weatherreport.mp3"
    }.get(x) 

def mp_self(x):
    return {
        "IMSI" : "imsi.mp3",
        "SONGDO" : "songdo.mp3",
        "XX" : "xx.mp3",
        "DEFAULT" : "weatherreport.mp3"
    }.get(x) 


def streamName(x):
    return {
        "IMSI" : "weatherReport_xx",
        "SONGDO" : "weatherReport_imsi",
        "XX" : "weatherReport_songdo",
        "DEFAULT" : "weatherreport_jingwan_wet_land"
    }.get(x) 

def streamName_self(x):
    return {
        "IMSI" : "weatherReport_imsi",
        "SONGDO" : "weatherReport_songdo",
        "XX" : "weatherReport_xx",
        "DEFAULT" : "weatherreport_jingwan_wet_land"
    }.get(x) 



def init():
    global PLACE
    global STREAM_MOUNTPOINT
    global STREAM_NAME
    # Read PLACE from outside script
    result = str(subprocess.check_output ('/bin/cat ' + SCRIPT_PATH + 'PLACE', shell=True))
    PLACE = result.split('\n')[0]
    # print PLACE
    STREAM_MOUNTPOINT = mp_self(PLACE)
    # print STREAM_MOUNTPOINT
    STREAM_NAME = streamName_self(PLACE)
    # print STREAM_NAME


# Callback functions for Adafruit.IO connections
def AIOconnected(client):
    # client.subscribe('alarms')
    print("Connected to Adafruit.IO")
    client.subscribe(feed_recVol(PLACE))
    client.subscribe("sudo_halt")

def AIOdisconnected(client):
    print("adafruit.io client disconnected!")

def AIOmessage(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.    
    print("adafruit.io received ", payload)
    if feed_id == feed_recVol(PLACE):
        result = subprocess.check_output ('sudo -u pi amixer sset \'IN3L Digital\'' + payload + '%', shell=True) # set rec volume
        result = subprocess.check_output ('sudo -u pi amixer sset \'IN3R Digital\'' + payload + '%', shell=True) # set rec volume
        result = subprocess.check_output ('sed -i "3s/.*/vol=' + payload + '/g" ' + SCRIPT_PATH + 'strs', shell=True) # save value
    elif feed_id == "sudo_halt":
        if payload == "1":
            subprocess.check_output ('sudo halt', shell=True)

def publishState_stream(monitorState):
    print monitorState
    client.publish(topic_str(PLACE), monitorState)
    print("Publishing to " + topic_str(PLACE) + ": " + monitorState)

def checkStr():

    r = requests.get(STREAM_CHECK_POINT)
    #print r
    global cur_r
    global prv_r    

    if (r.status_code != 200):
        publishState_stream("STREAMER : Streaming link has NOT OK response (" + r.status_code + ")")
    else:
        if STREAM_MOUNTPOINT not in r.content:
            cur_r = 0
            if (cur_r != prv_r):
                publishState_stream("STREAMER : " + STREAM_MOUNTPOINT + " is NOT streaming...")
            prv_r = cur_r


        else:
            cur_r = 1
            if (cur_r != prv_r):
                publishState_stream("STREAMER : mount point " + STREAM_MOUNTPOINT + " is streaming WELL.")
            prv_r = cur_r

    threading.Timer(10, checkStr).start()



########################
# Main
########################

if "__main__" == __name__:

    init()

    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Setup the callback functions defined above.
    client.on_connect    = AIOconnected 
    client.on_disconnect = AIOdisconnected
    client.on_message    = AIOmessage 

    # Connect to the Adafruit IO server.
    client.connect()

    # Now the program needs to use a client loop function to ensure messages are
    # sent and received.  There are a few options for driving the message loop,
    # depending on what your program needs to do.  


    # The first option is to run a thread in the background so you can continue
    # doing things in your program.client.loop_background()
    client.loop_background()

    checkStr()

    sys.exit(0)

