#!/bin/bash

echo ----- To do start up -----
amixer sset Master 90% & python /home/pi/bin/solarRPI/checkStrCheckMpd.py &
