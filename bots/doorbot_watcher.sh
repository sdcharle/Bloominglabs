#!/bin/bash
# 07-10-2014 / NTH / restart doorbot when it dies
PROC_NAME="net_doorbot"

PID=`ps -ef | grep "${PROC_NAME}" | grep -v grep | awk '{print $2}'`
echo "PID = $PID"
if [[ -z $PID ]];then
	# doorbot has died, restart it
        #echo "yo db was not in the house"
	logger -t doorbot "$PROC_NAME was found not running, restarting it"
	nohup /usr/bin/python /home/pi/Bloominglabs/bots/net_doorbot.py &
	sleep 60
fi
