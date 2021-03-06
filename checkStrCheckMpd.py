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
#ON_VALUE = " player is ON"
#OFF_VALUE = " player is OFF"

SCRIPT_PATH = "/home/pi/bin/solarRPI/"

cur_r = 0
prv_r = 0

cur_rr = 0
prv_rr = 0

########################
# Functions
########################

def topic_str(x):
    return {
        "IMSI" : "text_console",
        "SONGDO" : "text_console",
        "XX" : "text_console"
    }.get(x) 
    
def topic_play(x):
    return {
        "IMSI" : "text_console",
        "SONGDO" : "text_console",
        "XX" : "text_console"
    }.get(x) 

def feed_spkVol(x):
    return {
        "IMSI" : "spk_vol_0",
        "SONGDO" : "spk_vol_1",
        "XX" : "spk_vol_2"
    }.get(x) 

def mp(x):
    return {
        "IMSI" : "xx.mp3",
        "SONGDO" : "imsi.mp3",
        "XX" : "songdo.mp3"
    }.get(x) 

def streamName(x):
    return {
        "IMSI" : "weatherReport_xx",
        "SONGDO" : "weatherReport_imsi",
        "XX" : "weatherReport_songdo"
    }.get(x) 


def init():
    global PLACE
    global STREAM_MOUNTPOINT
    global STREAM_NAME
    # Read PLACE from outside script
    result = str(subprocess.check_output ('/bin/cat ' + SCRIPT_PATH + 'PLACE', shell=True))
    PLACE = result.split('\n')[0]
    STREAM_MOUNTPOINT = mp(PLACE)
    #print STREAM_MOUNTPOINT
    STREAM_NAME = streamName(PLACE)
    #print STREAM_NAME


# Callback functions for Adafruit.IO connections
def AIOconnected(client):
    # client.subscribe('alarms')
    print("Connected to Adafruit.IO")
    client.subscribe(feed_spkVol(PLACE))
    client.subscribe("sudo_halt")

def AIOdisconnected(client):
    print("adafruit.io client disconnected!")

def AIOmessage(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.    
    # print (payload)
    print("adafruit.io received ", payload)
    if feed_id == feed_spkVol(PLACE):
        result = subprocess.check_output ('amixer sset Master ' + payload + '%', shell=True) # set spk volume
        result = subprocess.check_output ('sed -i "3s/.*/vol=' + payload + '/g" ' + SCRIPT_PATH + 's', shell=True) # save value
    elif feed_id == "sudo_halt":
        if payload == "1":
            subprocess.check_output ('sudo halt', shell=True)
        


def publishState_stream(monitorState):
    client.publish(topic_str(PLACE), monitorState)
    print("Publishing to " + topic_str(PLACE) + ": " + monitorState)

def publishState_player(monitorState):
    client.publish(topic_play(PLACE), monitorState)
    print("Publishing to " + topic_play(PLACE) + ": " + monitorState)

def readyToPlay():
    result = subprocess.check_output ('mpc clear', shell=True)
    # print result
    result = subprocess.check_output ('mpc add ' + STREAM_BASE_URL + STREAM_MOUNTPOINT, shell=True)
    # print result
    result = subprocess.check_output ('mpc play', shell=True)
    # print result

def checkStr():
    r = requests.get(STREAM_CHECK_POINT)
    global cur_r
    global prv_r    
    global cur_rr
    global prv_rr

    # print r
    if (r.status_code != 200):
        publishState_stream("PLAYER : Streaming link has NOT OK response (" + r.status_code + ")")
        # print ("PLAYER : Streaming link has NOT OK response (" + r.status_code + ")")
    else:
        # STREAM_MOUNTPOINT = mp(PLACE)
        if STREAM_MOUNTPOINT not in r.content:

            cur_r = 0
            if (cur_r != prv_r):
                publishState_stream("PLAYER : mount point " + STREAM_MOUNTPOINT + " not found.")
                # print ("PLAYER : mount point " + STREAM_MOUNTPOINT + " not found.")

                # Send MPD status
                msg = "PLAYER : " +  STREAM_BASE_URL + STREAM_MOUNTPOINT + "not found."
                publishState_player(msg)

            prv_r = cur_r


        else:
            result = subprocess.check_output ('mpc current', shell=True) # !!mpd must be running before do this.
            #print result

            subprocess.check_output ('mpc play', shell=True)

            if STREAM_NAME in result: # Playing already
                cur_rr = 1
                if (cur_rr != prv_rr):
                    msg = "PLAYER : " + STREAM_BASE_URL + STREAM_MOUNTPOINT + " is playing."
                #    print msg
                    publishState_player(msg)
                prv_rr = cur_rr

            else :
                cur_rr = 0
                if (cur_rr != prv_rr):
                    msg = "PLAYER : " + STREAM_BASE_URL + STREAM_MOUNTPOINT + " is NOT playing!!"
                #    print msg
                    publishState_player(msg)
                    readyToPlay()
                prv_rr = cur_rr

            cur_r = 1
            if (cur_r != prv_r):
                publishState_stream("PLAYER : mount point " + STREAM_MOUNTPOINT + " is streaming well.")
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

    readyToPlay()
    checkStr()

    sys.exit(0)

