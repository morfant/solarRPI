#!/bin/bash

vol=50

echo ----- To do start up -----
amixer sset IN3L $vol% & amixer sset IN3R $vol% & python /home/pi/bin/solarRPI/streamerControl.py &