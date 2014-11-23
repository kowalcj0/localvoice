#!/usr/bin/env bash

# kill the player
killall mpg321
# kill the server
pkill -f "python ./lvsrv.py"

cd /home/pi/lv \
        && {
                echo "Starting Local Voice Service"
                nohup ./lvsrv.py &
        }
