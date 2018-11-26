#!/bin/sh

cd /home/pi/autofahn_server
export LD_LIBRARY_PATH=/home/pi/autofahn_server/mjpg-streamer-experimental/
cd mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
./mjpg_streamer -o "output_http.so -w ./www" -i "input_raspicam.so" &
