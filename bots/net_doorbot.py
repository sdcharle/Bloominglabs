"""
SDC 1/11/2012

Bot that says 'hi' on IRC channel when people are authenticated by the RFID

messages have the form:
18:50:21  1/11/12 WED 18:50:21  1/11/12 WED User 14 authenticated.
18:50:21  1/11/12 WED User  granted access at reader 1


1/12/2012

Note, this is fun, reads the msgs in a voice usin festival

http://brainwagon.org/2011/01/30/my-speech-bot-using-irclib-py/
he has some great Arduino/hacker stuff, too

irclib code is here:

http://forge.kasey.fr/projets/hashzor/irclib.py

1/14/2012
SDC
Using 'select' so pings are handled.
Note they say poll may be better here:
http://docs.python.org/library/select.html

for testing use 'UNREAL'
sudo ./unreal in the Unreal dir
wooty.

note while testing if you add to the thing and save it goes back to the beginning of the file
try the test w/ a 'feeder

3/1/2012 SDC
Database!

Note, depending where this 'lives', you will need to change DATABASE_NAME and ACCESS_LOG_FILE appropriately

to-do - don't get caught in a loop ('cool off')

3/12/2012

TO-DO

Pushing box integration (table of notifications to send - notify the iPhone)
Auto-start on boot up.
remember the pogobox is now bloominglabs.no-ip.org

3/15/2012 SDC
PushingboxNotification up in here!

5/27/2012 SDC
RFID is now networked. Instead of reading a file, read a socket.

7/15/2012 SDC
Don't forget pachube yo

TODO - net (IRC) connectivity.
WTF w/ nohup?
general error handlin

"""

import logging
import subprocess, select
import irclib, random
import time, urllib, urllib2, simplejson
import time
from datetime import datetime
import re, sys, os

# for network piece
import socket
from pachube_updater import *

pac = Pachube('/v2/feeds/53278.xml')

# set DJANGO_SETTINGS_MODULE
#os.putenv('DJANGO_SETTINGS_MODULE','web_admin.settings')
os.environ['DJANGO_SETTINGS_MODULE'] ="settings"
from django.conf import settings

from pushingbox import pushingbox



# port where the RFID server is running. put this in settings.py for the django
# server
RFID_PORT = settings.RFID_PORT
RFID_HOST = settings.RFID_HOST

ACCESS_LOG_FILE = '~/Bloominglabs/open_access_scripts/access_log.txt'

#settings.configure(
#    DATABASE_ENGINE    = "sqlite3",
#    DATABASE_NAME      = "/Users/scharlesworth/BloomingLabs/web_admin/BloomingLabs.db",
#    INSTALLED_APPS     = ("doorman",)
#)
# note, you need to setup the above before importing modules etc
from django.db import models
from doorman.models import UserProfile, AccessEvent, SensorEvent, PushingboxNotification

logger = logging.getLogger('rfid_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('rfid.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("RFID logger bot started.")

IRC_SERVER =  'irc.bloominglabs.org' 
#IRC_SERVER = 'stephen-charlesworths-macbook-pro.local'
#IRC_SERVER = '127.0.0.1'

IRC_PORT = 6667
IRC_NICK = 'doorbot_net'
IRC_NAME = 'Bloominglabs RFID Door System thing'
IRC_CHANNEL = "#blabs-bots"

random.seed()
max_sleep = 3 # 'take a breath' after responding. prevent bots from making
# you make a damn fool of yourself

# %s - pass in name
random_sez = [
    'how about that local sports team, %s?',
    'hey there %s, let me get the door for you',
    'good day to you, %s',
    'great day for hacking there, %s',
    '%s in the hizous!',
    '%s has arrived',
    'Never fear, %s is here',
]

authpat =  re.compile("User (\d+) authenticated.", re.M)
# add sensor regexp
sensorpat = re.compile('Zone (\d+) sensor activated', re.M)
# last command
last_command_pat = re.compile('last\s+(\d+|\s*)\s*(\S+)', re.M and re.IGNORECASE)

# just look for access message, if so gimme the user
def check_for_door(stuff):
    match = authpat.search(stuff)
    if match:
        return match.group(1)
    else:
        return None
    
def check_for_sensor(stuff):
    match = sensorpat.search(stuff)
    if match:
        return match.group(1)
    else:
        return None    

def check_for_last_command(stuff):
    match = last_command_pat.search(stuff)
    if match:
        return match.groups()
    else:
        return None

def last_command_responses(stuff):
    matches = check_for_last_command(stuff)
    num = 1
    responses = []
    if not matches:
        return responses
    try:
        num = int(matches[0])
        if num > 10:
            num = 10 # don't flood the channel, son
    except:
        pass
    if matches[1] == 'sensor':
        qs = SensorEvent.objects.order_by('-event_date')[:num]
        for q in qs:
            responses.append('%s with value %s from sensor %s at %s' % (q.event_type, q.event_value, q.event_source, q.event_date))
    elif matches[1] == 'access':
        qs = AccessEvent.objects.order_by('-event_date')[:num]
        for q in qs:
            responses.append('%s at %s' % (q.user.username, q.event_date))
    else:
        responses = ('Command not understood. Types are ''sensor'' or ''access'', you asked for %s' % matches[1],)
    return responses
    

# like before but now both use these

def handle_msg(client, event, target):

    stuff = ','.join(event.arguments())
    said = event.arguments()[0]

    (name,truename) = event.source().split('!')

    time.sleep(random.choice(range(max_sleep)))
    try:
        if stuff.upper().find(IRC_NICK.upper()) >= 0:
            if stuff.find('get lost')>=0:
                client.disconnect('AAGUUGGGHHHHHHuuaaaaa!')
                logger.info("Fuck it, I disconnected")
            else:
                client.privmsg(target,u'%s, %s' % ('Type ''last n access'' or ''last n sensor'' to see recent accesses or sensors',name))
# handle last command (if anything came back)
        else:
            for r in last_command_responses(stuff):
                client.privmsg(target,u'%s' % r)

    except Exception, val:
        logger.error("fail in pubmsg handle: (%s) (%s)" % (Exception, val))
        
def handle_privmsg(client, event):
    handle_msg(client,event, (event.source().split('!'))[0])

    
"""
kind of a big deal. handler of all msgs!
"""

def handle_pubmsg(client, event):
    handle_msg(client, event, IRC_CHANNEL)
        
def handle_join(client,event):
        (name,truename) = event.source().split('!')  
        client.privmsg(IRC_CHANNEL,'%s!!!' % name.upper())

# only get stuff if there is in fact stuff to get
def get_log_line(p):                                                                                                              
    r, w, x = select.select([p.stdout.fileno()],[],[],1.0)
    if r:
        return p.stdout.readline()
    else:
        return None

def log_door_event(connection, user_id):
    prof = None
    try:
        prof = UserProfile.objects.get(rfid_slot = user_id)
    except:
        logger.error("Strange: no username found in DB for user %s." % user_id)
    username = 'UNKNOWN'
    if prof:
        # note can't log unknow this way, though
        event = AccessEvent(user = prof.user)
        event.save()
        username = prof.user.username   
    logger.info("we see: %s aka %s" % (user_id, username))
    msg = random_sez[random.choice(range(len(random_sez)))] % username
    connection.privmsg(IRC_CHANNEL,msg)
    pushingbox_notify(username)

def pushingbox_notify(username):
    pbns = PushingboxNotification.objects.filter(notification_type = 'Access')

    for p in pbns:   
        pushingbox(p.notification_devid, {'user':username})
    
def log_sensor_event(connection, sensor_id):
    event = SensorEvent(event_type = 'Motion', event_source = sensor_id, event_value = 1)
    event.save()

    
"""
Main program, fields messages
TO-DO: handle 'last visit' and 'last sensor' commands
"""
if __name__ == '__main__':
    irc = irclib.IRC()
    server = irc.server()
    
    ircConn = server.connect(IRC_SERVER,IRC_PORT,IRC_NICK,ircname= IRC_NAME)
    ircConn.join(IRC_CHANNEL)
    ircConn.add_global_handler('privmsg',handle_privmsg, -1)
    ircConn.add_global_handler('pubmsg',handle_pubmsg, -1)
    ircConn.add_global_handler('join',handle_join, -1)
    
    print "I'm live."
    logger.info("Started RFID logger.")
#    p = subprocess.Popen("tail -0f %s" % ACCESS_LOG_FILE, shell=True, stdout=subprocess.PIPE)

    # connect up in this piece
    rfid_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    rfid_client.connect((RFID_HOST,RFID_PORT))

    stringy = ''
    while True:
	doorval = 0
	officeval = 0
 # Wait for input from stdin & socket 1 is timeout
        input_ready, output_ready,except_ready = select.select([rfid_client], [],[],1)
        while input_ready:
        # you could have multiple
            for i in input_ready:
                if i == rfid_client:
                    charry = rfid_client.recv(1)
                    stringy = stringy + charry
                    uid = check_for_door(stringy)
                    if uid:
			doorval = 1
                        log_door_event(ircConn, uid)
                        time.sleep(3)
                        stringy = ''
                    sid = check_for_sensor(stringy)
                    if sid:
			officeval = 1
                        log_sensor_event(ircConn, sid)
                        stringy = ''

            input_ready, output_ready,except_ready = select.select([rfid_client], [],[],1)
        print "woot"
        try:
            pac.log('Door', doorval)
            ircConn.pong(IRC_CHANNEL)
            pac.log('Office',officeval)
	    print "doorlog be good"
        except Exception, val:
	    print "cosm probs: %s, %s" % (Exception, val)
            logger.error("Pachube update problems: %s:%s" % (Exception, val))
	irc.process_once(5) # timeout is 5

