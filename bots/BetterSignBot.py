#!/usr/bin/env python
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
import sys
import re
import time
import alphasign
from alphasign.modes import *
import random

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

"""

handles queueing shit up.

first just have a queue of 10 that 

to do - changes to modes, colors, etc.

general notes:

string file has 125 max

"""

USB_PORT = '/dev/serial/by-id/usb-FIDI_usb_serial_converter_FTCBW2W2-if00-port0'

class Sign():
  
  def __init__(self, usb_port = USB_PORT, max_size = 10):
    self.messages = []
    self.sign = alphasign.Serial(USB_PORT)
    # where in the queue are we?
    self.index = 0
    # where do we start
    self.start_index = 0
        
    self.sign.connect()
    self.sign.clear_memory()

    # how many 'live' messages do we have?
    self.size = 0
    self.max_size = max_size
    label_num = 0    
    for i in range(self.max_size):
      msg = {}
      
      msg["str"] = alphasign.String(size = 125, label = chr(ord('A') + label_num)) 
      label_num = label_num + 1
      msg["txt"] = alphasign.Text("%s%s" % (alphasign.colors.GREEN,msg["str"].call()), chr(ord('A') + label_num), mode = alphasign.modes.ROTATE)
      label_num = label_num + 1
      self.messages.append(msg)
      self.sign.allocate((msg["str"], msg["txt"]))
      self.sign.write(msg["str"])
      self.sign.write(msg["txt"])
      print "alloc'ed: %s string, %s text" % (
msg["str"], msg["txt"])

# note, ensure wrap-around working properly here      
  def addMessage(self,messageText):
    message = self.messages[self.index]
    message["str"].data = messageText
    self.sign.write(message["str"])
    self.index = (self.index + 1) % self.max_size
    self.size = self.size + 1
    if self.size > self.max_size:
      self.size = self.max_size
      self.start_index = (self.start_index + 1) % self.max_size # dropped the last one off the beginning
    run_sequence = []
    for i in range(self.size):
      run_sequence.append(self.messages[(self.start_index + i) % self.max_size]["txt"])
    self.sign.set_run_sequence(run_sequence)  
    print "sequence is:" 
    print  run_sequence  
    print "messages: " 
    print self.messages

  # could do below or could do clear mem against sign
  def clear(self):
    self.index = 0
    self.size = 0
    self.start_index = 0
    self.sign.set_run_sequence(())
    
  def updateMessage(self,label,message):
    pass
  
  def removeMessage(self,label):
    pass      

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
    self.sign = alphasign.Serial('/dev/tty.usbserial-FTCBW2W2')
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
#  nickname = 'SignBot'
#  channel = 'blabs-bots'
#  password = ''
#  reactor.connectTCP('irc.bloominglabs.org', 6667, SignBotFactory('#' + channel, nickname, password))
#  reactor.run()a
  sign = Sign(usb_port = USB_PORT) #, max_size = 1)
  sign.addMessage("Eat")
  sign.addMessage("at")
  sign.addMessage("Joe's")
