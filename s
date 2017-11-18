#!/bin/bash

vol=90

echo ----- To do start up -----
amixer sset Master $vol% & python /home/pi/bin/solarRPI/checkStrCheckMpd.py &
