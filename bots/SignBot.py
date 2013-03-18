#!/usr/bin/env python
# SDC in the place to B
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import sys
import re
import time
import alphasign
from alphasign.modes import *
import random
USB_PORT = "/dev/serial/by-id/usb-FIDI_usb_serial_converter_FTCBW2W2-if00-port0"

modes = [TWINKLE,
           SPARKLE,
           SNOW,
           INTERLOCK,
           SWITCH,
           SPRAY,
           STARBURST,
           WELCOME,
           SLOT_MACHINE,
           THANK_YOU,
           RUNNING_ANIMAL,
           FIREWORKS,
           TURBO_CAR,
           BALLOON_ANIMATION,
           CHERRY_BOMB,
           ROTATE,
           HOLD,
           ROLL_UP,
           ROLL_DOWN,
           ROLL_LEFT,
           ROLL_RIGHT,
           WIPE_UP,
           WIPE_DOWN,
           WIPE_LEFT,
           WIPE_RIGHT,
           SCROLL,
           AUTOMODE,ROLL_IN,
           ROLL_OUT,
           WIPE_IN,
           WIPE_OUT,
           COMPRESSED_ROTATE,
           EXPLODE
           ]

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
    self.sign = alphasign.Serial(USB_PORT)
    self.sign.connect()
    self.sign.clear_memory()
    self.message_str = alphasign.String(size = 140, label = "2")
    self.message_txt = alphasign.Text("%s" % self.message_str.call(), label="B", mode = alphasign.modes.TWINKLE)
    #message_txt = alphasign.Text("%s%s" % (alphasign.colors.GREEN,message_str.call()), label="B", mode = alphasign.modes.ROTATE)
    self.message_str.data = "Make me say things!"
    # allocate memory for these objects on the sign
    self.sign.allocate((self.message_str, self.message_txt ))
    self.sign.set_run_sequence((self.message_txt,))

    self.sign.write(self.message_txt)
    self.sign.write(self.message_str)
    
  def writeMessage(self,message):
    self.message_str.data = message
    mode = modes[random.randrange(len(modes))]
    self.message_txt.mode = mode
    self.sign.write(self.message_txt)
    self.sign.write(self.message_str)
    
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
