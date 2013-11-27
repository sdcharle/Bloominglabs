"""
7/16/2013 SDC
just here to log LAZZOR time.
scan the network for something on port 12345

7/20/2013 SDC
now use 192.168.1.5
better logging
"""
import logging
import subprocess, select
import irclib, random
import time, urllib, urllib2, simplejson
import time
import re, sys, os
import datetime
# for future investigation - weirdly from datetime import datetime didn't work!
# for network piece
import socket
sys.path.append('/Users/scharlesworth/Bloominglabs/web_admin')
from pachube_updater import *
import sys

LAZZOR_PORT = 12345
# sounds like a port an idiot would use for his luggage
CHECK_INTERVAL = 60 # seconds between checks
LAST_LAZZOR_IP = 149 # start here. Wheel around! Check every 30 seconds

pac = Pachube('/v2/feeds/53278.xml')

last_check_time = datetime.datetime.now()

logger = logging.getLogger('laser_logger')
logger.setLevel(logging.WARNING)
fh = logging.FileHandler('laser.log')
fh.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("Lazer Loggins logger bot started.")

"""
API:

STATUS
IDLE
102 OK

When Job is running:

0 DOWN
1 IDLE
2 RUNNING
"""

def get_lazzor_status():
    global LAST_LAZZOR_IP # so much for constant
    status = None
    for i in range(256):
        try: 
            logger.info('try ip: 192.168.1.%i' % ((LAST_LAZZOR_IP + i) % 256))
            conn = socket.create_connection(('192.168.1.%i' % ((LAST_LAZZOR_IP + i) % 256), LAZZOR_PORT),1)
            conn.sendall('STATUS\n')
            status = conn.recv(1024)
            while status:
                if status.find('Hello')>-1:
                    status = conn.recv(1024)
                    #print "Yo we are in status: %s" % status
                    LAST_LAZZOR_IP = (LAST_LAZZOR_IP + i) % 256 # update it.
                    conn.close()
                    return status
                else:
                    status = conn.recv(1024)
        except Exception, val:
            pass # only log if not timeout?
            logger.warning('Exc: %s, val: %s keep going' % (Exception, val))
    return 'DOWN'

if __name__ == '__main__':

    logger.info("Started lazzor logger.")
    # connect up in this piece
    while True:
        # try last thing we used, if we failed wheel that shit around
        status = get_lazzor_status()
        
        lc = 0
        if status.find('IDLE') > -1:
            lc = 1
        elif status.find('RUNNING') > -1:
            lc = 2
        try:
            pac.log('LaserCutter', lc)
        except Exception, val:
            logger.warning("aw shit Xively prob: %s - %s" % (Exception, val))
        time.sleep(CHECK_INTERVAL)
