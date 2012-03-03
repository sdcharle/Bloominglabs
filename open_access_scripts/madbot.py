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

1/25/2012
Put some AIML up in this

"""

import logging
import subprocess, select
import irclib, random
import sys
import time, urllib, urllib2, simplejson
import time
from datetime import datetime
import re
import aiml
k = aiml.Kernel()
k.setBotPredicate("name","madbot")
k.setPredicate("name","dude")
k.learn("std-startup.xml")
k.respond("load aiml b")

ACCESS_LOG_FILE = 'access_log.txt'
logger = logging.getLogger('mad_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('mad.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("RFID logger bot started.")

# this is a dumb temporary user number to user mapping
# current as of 1/14/2012, but seriously, centralize this shit.
db = {
    '0':'dosman',
    '1':'steve',
    '14':'nick',
    '13':'daniel',
    '12':'david b.',
    '4':'jay',
    '2':'jenett',    
}


#IRC_SERVER =  'irc.bloominglabs.org' 
#IRC_SERVER = 'stephen-charlesworths-macbook-pro.local'
IRC_SERVER = '127.0.0.1'

IRC_PORT = 6667
IRC_NICK = 'madbot'
IRC_NAME = 'Bloominglabs RFID Door System thing'
IRC_CHANNEL = "#hackerspace"

random.seed()
max_sleep = 3 # 'take a breath' after responding. prevent bots from making
# you make a damn fool of yourself

# %s - pass in name
random_sez = [
    'how about that local sports team, %s?',
    'hey there %s, let me get the door for you',
    'good day to you, %s',
    'great day for hacking there, %s',
]

authpat =  re.compile("User (\d+) authenticated.", re.M)

# just look for access message, if so gimme the user
def check_for_door(stuff):
    match = authpat.search(stuff)
    if match:
        return match.group(1)
    else:
        return None

def handle_privmsg(client, event):
    stuff = ','.join(event.arguments())
    time.sleep(random.choice(range(max_sleep)))
# note but what is name
    try:
        (name,truename) = event.source().split('!')
        client.privmsg(name,'I got no secrets')
    except Exception, val:
        logger.error("weird privmsg fail! (%s) : (%s)" % (Exception, val))
    
def handle_action(client, event):
    client.privmsg(IRC_CHANNEL,'I see what you did there...')
    stuff = ','.join(event.arguments())
    (name,truename) = event.source().split('!')
    print "%s: %s" % (name,stuff) 

"""
kind of a big deal. handler of all msgs!
"""

def handle_pubmsg(client, event):
    stuff = ','.join(event.arguments())
    said = event.arguments()[0]
    sayit = ''
    (name,truename) = event.source().split('!')

    time.sleep(random.choice(range(max_sleep)))
    try:
        logger.info("%s: %s" % (name, stuff))
        if stuff[0] == "'":
            #specify session (third arg) or it does not take
            k.setPredicate("name",name, name)
            sayit = k.respond(stuff[1:], name)
                
        elif stuff.upper().find(IRC_NICK.upper()) >= 0:
            if stuff.find('get lost')>=0:
                client.disconnect('AAGUUGGGHHHHHHuuaaaaa!')
                logger.info("Fuck it, I disconnected")
                sys.exit(0)
            else:
                sayit = 'Type a single quote at the beginning of your message to talk to me.'
        if sayit:
            sayit = sayit[:400] # protect against the 'too long' thing
            client.privmsg(IRC_CHANNEL,sayit)
            logger.info("%s: %s" % (IRC_NICK, sayit) )
    except Exception, val:
        logger.error("fail in pubmsg handle: (%s) (%s)" % (Exception, val))
        
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
        
if __name__ == '__main__':
    irc = irclib.IRC()
    server = irc.server()
    
    ircConn = server.connect(IRC_SERVER,IRC_PORT,IRC_NICK,ircname= IRC_NAME)
    ircConn.join(IRC_CHANNEL)
    ircConn.add_global_handler('privmsg',handle_privmsg, -1)
    ircConn.add_global_handler('pubmsg',handle_pubmsg, -1)
    ircConn.add_global_handler('action',handle_action, -1)
    ircConn.add_global_handler('join',handle_join, -1)
    print "Shaolin runnin it son. I'm live."
    logger.info("Started RFID logger.")
    p = subprocess.Popen("tail -0f %s" % ACCESS_LOG_FILE, shell=True, stdout=subprocess.PIPE)
    stringy = ''
    while True:
        r, w, x = select.select([p.stdout.fileno()],[],[],1.0)
        while r:
            charry = p.stdout.read(1)
            stringy = stringy + charry
            uid = check_for_door(stringy)
            if uid:
                if db.has_key(uid):
                    logger.info("we see: %s aka %s" % (uid, db[uid]))
                    msg = random_sez[random.choice(range(len(random_sez)))] % db[uid]
                    ircConn.privmsg(IRC_CHANNEL,msg)
                    time.sleep(3)
                stringy = ''
            r, w, x = select.select([p.stdout.fileno()],[],[],1.0)
        irc.process_once(5) # timeout is 5
