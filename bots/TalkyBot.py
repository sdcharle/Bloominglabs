#!/usr/bin/env python
"""
Implementation of Wolfman Jack Technology plus more
7/14/2013 SDC
"""
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import sys
import re
import time
import subprocess
import botconfig

cleanPat = re.compile("[\'\"\;]")
NICK = "TalkyBot"

def playMP3(file):
    p = subprocess.Popen("sleep 2; mpg123 %s" % file, shell=True, stdout=subprocess.PIPE)
  
class TalkyBot(irc.IRCClient):

  def _get_nickname(self):
    return self.factory.nickname
  nickname = property(_get_nickname)

  def clean(self, msg):
    if cleanPat.search(msg):
      self.msg(self.factory.channel,'Nice try, jackass.')
      msg = cleanPat.sub(' ', msg)
    return msg
  
  def talk(self,msg):
    # take out questionable shit
    msg = self.clean(msg)
    print msg
    p = subprocess.Popen("echo ' %s' | festival --tts" % msg, shell=True, stdout=subprocess.PIPE)
    
  def signedOn(self):
    self.join(self.factory.channel, self.factory.password)
    print "Signed on as %s." % (self.nickname,)

  def joined(self, channel):
    print "Joined %s." % (channel,)

  def privmsg(self, user, channel, msg):  
    if msg.startswith('!t '):
      self.talk(' '.join(msg.split(' ')[1:]))
      return
    if not user:
      return
    if msg.startswith('!s') and user.find('doorbot')>=-1:
      playMP3("wolfman.mp3")
    elif self.nickname in msg:
      msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)      
      prefix = "%s: " % (user.split('!', 1)[0], )
      self.helpMsg()
    
  def helpMsg(self):
    self.msg(self.factory.channel,"Type !t something and I'll announce it.")
    
class TalkyBotFactory(protocol.ClientFactory):
  protocol = TalkyBot

  def __init__(self, channel, nickname, password=''):
    self.channel = channel
    self.nickname = nickname
    self.password = password
    
  def clientConnectionLost(self, connector, reason):
    print "Lost connection (%s), reconnecting." % (reason,)
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    print "Could not connect: %s" % (reason,)

if __name__ == "__main__":
#  nickname = 'TalkyBot'
#  channel = 'blabs-bots'
#  server = '127.0.0.1'
#  global NICK
  password = ''
  reactor.connectTCP(botconfig.SERVER, botconfig.PORT,TalkyBotFactory('#' + botconfig.CHANNEL, NICK, password))
  reactor.run()
