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



########################
# Globals
########################

ADAFRUIT_IO_USERNAME = "giy"        # Adafruit.IO user ID
ADAFRUIT_IO_KEY = "c0ee9df947d4443286872f667e389f1f"    # Adafruit.IO user key
ADAFRUIT_IO_TOPIC = "info"        # Adafruit.IO alarm topic

STREAM_MOUNTPOINT = "weatherreport_test.ogg"
STREAM_CHECK_POINT = "http://weatherreport.kr:8000/status-json.xsl"

cur_r = 0
prv_r = 0

########################
# Functions
########################

# Callback functions for Adafruit.IO connections
def AIOconnected(client):
    # client.subscribe('alarms')
    print("Connected to Adafruit.IO")
    # client.subscribe(ADAFRUIT_IO_TOPIC)

def AIOdisconnected(client):
    print("adafruit.io client disconnected!")

def AIOmessage(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.    
    print("adafruit.io received ", payload)

def publishState(monitorState):
    print("Publishing to " + ADAFRUIT_IO_TOPIC + ": " + monitorState)
    client.publish(ADAFRUIT_IO_TOPIC, monitorState)


def checkStr():
    r = requests.get(STREAM_CHECK_POINT)
    global cur_r
    global prv_r    
    # print r
    if (r.status_code != 200):
        publishState("INFO : Streaming link has NOT OK response (" + r.status_code + ")")
        # print ("INFO : Streaming link has NOT OK response (" + r.status_code + ")")
    else:
        if STREAM_MOUNTPOINT not in r.content:

            cur_r = 0
            if (cur_r != prv_r):
                publishState("INFO : mount point " + STREAM_MOUNTPOINT + " not found.")
                # print ("INFO : mount point " + STREAM_MOUNTPOINT + " not found.")
            prv_r = cur_r
        else:
            cur_r = 1
            if (cur_r != prv_r):
                publishState("INFO : mount point " + STREAM_MOUNTPOINT + " is streaming well.")
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

    checkStr()

    sys.exit(0)

