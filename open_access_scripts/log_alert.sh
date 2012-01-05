#!/bin/bash
cd /home/access/open_access_scripts
tail -0f /home/access/open_access_scripts/access_log.txt | egrep --line-buffered -i "triggered" |
while read line
        do
                msmtp -t < /home/access/open_access_scripts/alert_msg.txt
        done