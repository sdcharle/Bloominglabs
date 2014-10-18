#!/usr/bin/env python
# SDC in the place to B
import sys
import re
import time
import alphasign
from alphasign.modes import *
import random
USB_PORT = "/dev/tty.usbserial-A500STEQ"

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

class SignBotFactory():

  def __init__(self):
    self.sign = alphasign.Serial(USB_PORT)
    self.sign.connect()
#    self.sign.clear_memory()
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
    
if __name__ == "__main__":
  sbf = SignBotFactory()
  while True:
    say = raw_input()
    sbf.writeMessage(say)

