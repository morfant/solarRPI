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

ADAFRUIT_IO_USERNAME = "giy"        # Adafruit.IO user ID
ADAFRUIT_IO_KEY = "c0ee9df947d4443286872f667e389f1f"    # Adafruit.IO user key
ADAFRUIT_IO_TOPIC_0 = "info"        # Adafruit.IO alarm topic
# ADAFRUIT_IO_TOPIC_streamer = "stream_0"        # Adafruit.IO alarm topic
ADAFRUIT_IO_TOPIC_streamer = "stream_1"        # Adafruit.IO alarm topic
# ADAFRUIT_IO_TOPIC_streamer = "stream_2"        # Adafruit.IO alarm topic
# ADAFRUIT_IO_TOPIC_player = "player_0"        # Adafruit.IO alarm topic
ADAFRUIT_IO_TOPIC_player = "player_1"        # Adafruit.IO alarm topic
# ADAFRUIT_IO_TOPIC_player = "player_2"        # Adafruit.IO alarm topic

STREAM_BASE_URL = "http://weatherreport.kr:8000/"
# STREAM_MOUNTPOINT = "weatherreport.mp3"
# STREAM_MOUNTPOINT = "imsi.mp3"
STREAM_MOUNTPOINT = "songdo.mp3"
# STREAM_MOUNTPOINT = "xx.mp3"
# STREAM_NAME = "weatherReport_imsi" # 1
STREAM_NAME = "weatherReport_songdo" # 2
# STREAM_NAME = "weatherReport_xx" # 3
STREAM_CHECK_POINT = "http://weatherreport.kr:8000/status-json.xsl"

cur_r = 0
prv_r = 0

cur_rr = 0
prv_rr = 0

########################
# Functions
########################

# Callback functions for Adafruit.IO connections
def AIOconnected(client):
    # client.subscribe('alarms')
    print("Connected to Adafruit.IO")
    # client.subscribe(ADAFRUIT_IO_TOPIC_0)

def AIOdisconnected(client):
    print("adafruit.io client disconnected!")

def AIOmessage(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.    
    print("adafruit.io received ", payload)

def publishState_stream(monitorState):
    print("Publishing to " + ADAFRUIT_IO_TOPIC_0 + ": " + monitorState)
    client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)
    client.publish(ADAFRUIT_IO_TOPIC_streamer, monitorState)
    # client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)
    # client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)

def publishState_player(monitorState, onoff):
    print("Publishing to " + ADAFRUIT_IO_TOPIC_0 + ": " + monitorState)
    client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)
    client.publish(ADAFRUIT_IO_TOPIC_player, onoff)
    # client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)
    # client.publish(ADAFRUIT_IO_TOPIC_0, monitorState)

def readyToPlay():
    result = subprocess.check_output ('mpc clear', shell=True)
    print result
    result = subprocess.check_output ('mpc add ' + STREAM_BASE_URL + STREAM_MOUNTPOINT, shell=True)
    print result
    result = subprocess.check_output ('mpc play', shell=True)
    print result

def checkStr():
    r = requests.get(STREAM_CHECK_POINT)
    global cur_r
    global prv_r    
    global cur_rr
    global prv_rr

    # print r
    if (r.status_code != 200):
        publishState_stream("INFO : Streaming link has NOT OK response (" + r.status_code + ")")
        # print ("INFO : Streaming link has NOT OK response (" + r.status_code + ")")
    else:
        if STREAM_MOUNTPOINT not in r.content:

            cur_r = 0
            if (cur_r != prv_r):
                publishState_stream("INFO : mount point " + STREAM_MOUNTPOINT + " not found.")
                # print ("INFO : mount point " + STREAM_MOUNTPOINT + " not found.")
            prv_r = cur_r

            # Send MPD status
            cur_rr = 0
            if (cur_rr != prv_rr):
                msg = "STOPPED : Check " + STREAM_BASE_URL + STREAM_MOUNTPOINT + "!!"
                # print msg
                publishState_player(msg, 0)
            prv_rr = cur_rr


        else:
            result = subprocess.check_output ('mpc current', shell=True) # !!mpd must be running before do this.
            # print result
            if STREAM_NAME in result: # Playing already
                cur_rr = 1
                if (cur_rr != prv_rr):
                    msg = "PLAYING OK : " + STREAM_BASE_URL + STREAM_MOUNTPOINT
                    print msg
                    publishState_player(msg, 1)
                prv_rr = cur_rr

            else :
                cur_rr = 0
                if (cur_rr != prv_rr):
                    msg = "STOPPED : Check " + STREAM_BASE_URL + STREAM_MOUNTPOINT + "!!"
                    print msg
                    publishState_player(msg, 0)
                    subprocess.call ('mpc play', shell=True)
                prv_rr = cur_rr

            cur_r = 1
            if (cur_r != prv_r):
                publishState_stream("INFO : mount point " + STREAM_MOUNTPOINT + " is streaming well.")
                # print ("INFO : mount point " + STREAM_MOUNTPOINT + " is streaming well.")
            prv_r = cur_r

    threading.Timer(10, checkStr).start()



########################
# Main
########################

if "__main__" == __name__:


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

