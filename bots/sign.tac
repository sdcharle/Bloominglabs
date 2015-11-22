"""
Network server for da sign
send messages to queue as:
JSON!

start twistd daemon:
http://www.tsheffler.com/blog/?p=526

4/6/2014
SDC
Last piece.
Looping call (1 minute)
Pull off the queue and display

possible to-dos
add client list
have clients identify themselves
add ability to list clients (command)

"""

from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from twisted.internet.task import LoopingCall

import sys
import time
import simplejson as sj

from SignQueue import SignQueue

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

# do a reactor stop?

class SignClient(LineReceiver):

    def connectionMade(self):
        log.msg('Connection received from tcp...')

    def connectionLost(self, reason):
        log.msg('Connection lost because: %s' % reason)

    def lineReceived(self, line):
        log.msg('Command received: %s' % repr(line))
        self.factory.queueMessage(line)
        #Build command, if ok, send to serial port

# note, what about things going down to s port tho.

class SignClientFactory(Factory):
    protocol = SignClient

    def __init__(self):
    # add alphaSign?
        self.sign_queue = SignQueue()
        self.sign = alphasign.Serial(USB_PORT)
        self.sign.connect()
        #self.sign.clear_memory()
        self.message_str = alphasign.String(size = 140, label = "2")
        self.message_txt = alphasign.Text("%s" % self.message_str.call(), label="B", mode = alphasign.modes.TWINKLE)
        #message_txt = alphasign.Text("%s%s" % (alphasign.colors.GREEN,message_str.call()), label="B", mode = alphasign.modes.ROTATE)
        self.message_str.data = "Make me say things!"
        # allocate memory for these objects on the sign
        self.sign.allocate((self.message_str, self.message_txt ))
        self.sign.set_run_sequence((self.message_txt,))
        # add Looping call to:
        # pull message off the queue and display it
        # (or: call later w/ lifetime?)
        self.looper = LoopingCall(self.changeDisplay)
        self.looper.start(15) # every 5

    def changeDisplay(self):
        print "time to change display"
        r = self.sign_queue.pullMessage()
        if r:
            self.writeMessage(r['message'])    
    
    def writeMessage(self,message):
        self.message_str.data = message
        mode = modes[random.randrange(len(modes))]
        self.message_txt.mode = mode
        self.sign.write(self.message_txt)
        self.sign.write(self.message_str)
    
    def queueMessage(self,message):
        log.msg("add message to queue")
        try:
            msg = sj.loads(message)
            if msg.has_key("message"):
                self.sign_queue.addMessage(msg)#["message"])
        except Exception, val:
            log.msg("json parse failed, fuck it, moving on: %s - %s" % (Exception, val))
    
    def establishConnection(self):
        # get reactor ref
        from twisted.internet import reactor
        log.msg("Establish connection called")

"""

Below we set up the twistd DAEMON!

"""

tcpfactory = SignClientFactory()

# q remains: do we specify reactor for USB or something else?
# will blow up if you can't open the port, though
# so this is using the same factory, however other clients attaching to the server can't seem to see this!

# put this in a retry loop? For how long?

tcpfactory.establishConnection()

# service stuff
application = service.Application("sign_network_server")
# note should do in settings.py
networkService = internet.TCPServer(6666, tcpfactory)
networkService.setServiceParent(application)
