#!/bin/sh

cd /home/pi/autofahn_server
export LD_LIBRARY_PATH=/home/pi/autofahn_server/mjpg-streamer-experimental/
/home/pi/autofahn_server/server_only_drive_save.py &
exit 0

