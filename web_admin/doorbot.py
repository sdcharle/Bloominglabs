
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

"""

import logging
import subprocess, select
import irclib, random
import time, urllib, urllib2, simplejson
import time
from datetime import datetime
import re, sys, os
# set DJANGO_SETTINGS_MODULE
os.putenv('DJANGO_SETTINGS','web_admin.settings')
from django.conf import settings

from pushingbox import pushingbox

ACCESS_LOG_FILE = '/home/access/scripts/access_log.txt'

settings.configure(
    DATABASE_ENGINE    = "sqlite3",
    DATABASE_NAME      = "/home/access/databases/BloomingLabs.db",
    INSTALLED_APPS     = ("doorman",)
)
# note, you need to setup the above before importing modules etc
from django.db import models
from doorman.models import UserProfile, AccessEvent, SensorEvent, PushingboxNotification

logger = logging.getLogger('rfid_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('/home/access/logs/rfid.log')
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
IRC_NICK = 'doorbot_jr'
IRC_NAME = 'Bloominglabs RFID Door System thing'
IRC_CHANNEL = "#blabs-bots"

random.seed()
max_sleep = 3 # 'take a breath' after responding. prevent bots from making
# you make a damn fool of yourself

# %s - pass in name
            responses.append('%s with value %s from sensor %s at %s' % (q.event_type, q.event_value, q.event_source, q.event_date))
    elif matches[1] == 'access':
        qs = AccessEvent.objects.order_by('-event_date')[:num]
        for q in qs:
            responses.append('%s at %s' % (q.user.username, q.event_date))
    else:
        responses = ('Command not understood. Types are \'sensor\' or \'access\', you asked for %s' % matches[1],)
    if not responses:
	responses = ('nothing to report',)
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

def log_door_event(connection, user_id):
    prof = None
    try:
        prof = UserProfile.objects.get(rfid_slot = user_id)
    except:
        logger.error("Strange: no username found in DB for user >%s<." % user_id)
    username = 'UNKNOWN'
    if prof:
        # note can't log unknow this way, though
        event = AccessEvent(user = prof.user)
        event.save()
        username = prof.user.username   
    logger.info("we see: %s aka %s" % (user_id, username))
    msg = random_sez[random.choice(range(len(random_sez)))] % username
 
#    p = subprocess.Popen("echo  %s | festival --tts" % msg, shell=True)

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
    server = irc.server()
    
    ircConn = server.connect(IRC_SERVER,IRC_PORT,IRC_NICK,ircname= IRC_NAME)
    ircConn.join(IRC_CHANNEL)
    ircConn.add_global_handler('privmsg',handle_privmsg, -1)
    ircConn.add_global_handler('pubmsg',handle_pubmsg, -1)
    ircConn.add_global_handler('join',handle_join, -1)
    
    print "I'm live."
    logger.info("Started RFID logger.")
    p = subprocess.Popen("tail -0f %s" % ACCESS_LOG_FILE, shell=True, stdout=subprocess.PIPE)
    stringy = ''
    while True:

