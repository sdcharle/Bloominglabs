#!/usr/bin/env python
# SDC in the place to B
"""
4/18/2014 SDC
new version uses Queue!


"""

import SignQueue
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import sys
import re
import time

class SignBot(irc.IRCClient):

  def _get_nickname(self):
    return self.factory.nickname
  nickname = property(_get_nickname)

  def signedOn(self):
    self.join(self.factory.channel, self.factory.password)
    print "Signed on as %s." % (self.nickname,)

  def joined(self, channel):
    print "Joined %s." % (channel,)

  def privmsg(self, user, channel, msg):
    if msg.startswith('!s '):
      print msg.split(' ')[1]
      self.factory.writeMessage(' '.join(msg.split(' ')[1:]))
      return
    elif not user:
      return
    elif self.nickname in msg:
      msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)
      prefix = "%s: " % (user.split('!', 1)[0], )
    else:
      prefix = ''

class SignBotFactory(protocol.ClientFactory):
  protocol = SignBot
  
  def __init__(self, channel, nickname, password=''):
    self.channel = channel
    self.nickname = nickname
    self.password = password
    self.signQueue = SignQueue.SignQueue()

  def writeMessage(self,message):
    self.signQueue.addMessage(message,immediate = 1)
    
  def clientConnectionLost(self, connector, reason):
    print "Lost connection (%s), reconnecting." % (reason,)
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    print "Could not connect: %s" % (reason,)

if __name__ == "__main__":
  nickname = 'SignBot'
  channel = 'blabs-bots'
  password = ''
  reactor.connectTCP('irc.bloominglabs.org', 6667, SignBotFactory('#' + channel, nickname, password))
  reactor.run()
