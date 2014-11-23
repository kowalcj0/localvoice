LOCAL VOICE
===========


# Scheduling
To refresh the list of things to play every N-minute we've decided to use 
a cron job that will execute refreshsrv.sh script.
Refreshsrv.sh script kills all running instances of lvsrv.py and mpg321 player.
Then it starts new lvsrv.py which updates its schedule on startup.
To configure the cron job run:

    sudo crontab -e

go to the EOF and add ie.:

    */5 * * * * /home/pi/lv/refreshsrv.sh

where 5 means that this job will be ran every 5 mins.


# start the service on pi boot up
You can also decide to start the service on device boot up.
To to it, edit:

    sudo vi /etc/rc.local

and add simple instruction like:

    cd /home/pi/lv \
            && {
                    echo "Starting Local Voice Service"
                    nohup ./lvsrv.py &
                    cd ..
            }

