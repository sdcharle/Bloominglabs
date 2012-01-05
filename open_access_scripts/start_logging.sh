#!/bin/bash
# Start logging functions
cd /home/access/scripts
/usr/bin/minicom -o --capturefile=/home/access/scripts/access_log.txt
/bin/su - access -c "/home/access/scripts/log_notify.sh &"
/bin/su - access -c "/home/access/scripts/log_alert.sh &"