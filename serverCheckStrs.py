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
ADAFRUIT_IO_TOPIC = ""
ON_VALUE = "1"
OFF_VALUE = "0"

PLACES = ["IMSI", "SONGDO", "XX"]
STREAM_CHECK_POINT = "http://weatherreport.kr:8000/status-json.xsl"

listenUrls = []
prev_listenUrls = None

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

def getMountPoint(x):
    return {
        "IMSI" : "xx.mp3",
        "SONGDO" : "imsi.mp3",
        "XX" : "songdo.mp3"
    }.get(x) 

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

def publishState_stream(monitorState, w):
    print("Publishing to " + topic_str(w) + ": " + monitorState)
    client.publish(topic_str(w), monitorState)

def publishState_player(onoff, w):
    print("Publishing to " + topic_play(w) + ": " + onoff)
    client.publish(topic_play(w), onoff)

def checkStr():
    global listenUrls
    global prev_listenUrls

    r = requests.get(STREAM_CHECK_POINT)
    dic = r.json()

    listenUrls[:] = []

    if 'source' in dic['icestats']:
        sources = dic['icestats']['source']
        lenSrc = len(sources)
        # print sources

        if lenSrc > 3 : # means it has 1 key
            listenUrls.append(sources['listenurl'].split('/')[-1])
        else : # means it has 2 or 3 keys
            for x in range(0, len(sources)):
                listenUrls.append(sources[x]['listenurl'].split('/')[-1])

    print listenUrls
    
    if listenUrls != prev_listenUrls:

        for w in PLACES: 
            mp = getMountPoint(w)
            # print "mp: " + mp

            if (r.status_code != 200):
                publishState_stream("JJWC : Streaming link has NOT OK response (" + r.status_code + ")", w)
                publishState_player("JJWC : player on " + mp + "is turned OFF.")
                
            else:
                if mp not in listenUrls:
                    publishState_stream("JJWC : Mount point " + mp + " not found.", w)
                    publishState_player("JJWC : player on " + mp + "is turned OFF.")

                else:
                    publishState_stream("JJWC : Mount point " + mp + " is streaming well.", w)
        
        # https://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list
        prev_listenUrls = listenUrls[:]

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

