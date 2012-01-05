#!/bin/bash
tail -0f /home/access/open_access_scripts/access_log.txt | egrep --line-buffered -i "authenticated" | while read line
        do
                rm /home/access/open_access_scripts/message_tmp.txt
                cp /home/access/open_access_scripts/log_msg.txt /home/access/open_access_scripts/message_tmp.txt
                sleep 1
                tail -6 /home/access/open_access_scripts/access_log.txt >> /home/access/open_access_scripts/message_tmp.txt
                msmtp -t < /home/access/open_access_scripts/message_tmp.txt
        done