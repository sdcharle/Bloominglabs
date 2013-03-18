"""

to dos:
add set time command (on RFID board)
is it possible for the service to detect if serial port is plugged in or comes back to life again?
time outs for connections


Client for serial port
in turn, a proxy forwards client req to serial and sends responses back to ALL clients


Things to use:
GPSFix - example of Serial port

Proxy???

Arduino guy w/ questions:
http://stackoverflow.com/questions/7134170/custom-python-twisted-protocol-good-practices-and-complexity

Some great serial examples:
http://stackoverflow.com/questions/4715340/python-twisted-receive-command-from-tcp-write-to-serial-device-return-response
(service w/ retries, state machine framework)

Arduino serial example!
http://nullege.com/codes/show/src%40o%40f%40office-weather-HEAD%40listener.py/21/twisted.internet.serialport.SerialPort/python
Notice he's using twisted.python usage function

This one is neat, has hardware detecting when serial connects
http://nullege.com/codes/show/src%40s%40p%40Sparked-0.6%40sparked%40hardware%40serial.py/14/twisted.internet.serialport.SerialPort/python

http://twistedmatrix.com/documents/current/core/howto/tutorial/protocol.html

above includes IRC reply bot! yeah!

5/20/12 - SDC
woo-hoo! works! now test to ensure clients don't clobber each other.
Actually hit it w/ a bunch of clients req. Surely it knows what comes from who, right?

5/26/2012 - SDC
Added some 'connection lost' handling
Add service capabilities



note also:
try:
    x = 1 / 0
except:
    log.err()   # will log the ZeroDivisionError
    
"""

from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
import sys

import time


# 1a21 is left port on laptop
# 1d11 is right port on laptop

class USBClient(LineReceiver): 

    def __init__(self, network):
        self.network = network
        self.USB_connected = False

    def connectionFailed(self):
        log.msg( "USB Connection Failed:" + repr(self))
        reactor.stop()

    def connectionMade(self):
        log.msg('Connected to USB port')
        self.USB_connected = True

    def lineReceived(self, line):
        log.msg("USB Line received: %s" % repr(line))
        self.network.notifyAll(line)

    def sendLine(self, cmd):
        log.msg("Command sent down: %s" % cmd)
        self.transport.write(cmd + "\r\n")

    def outReceived(self, data):
        log.msg("outReceived! with %d bytes!" % len(data))
        self.data = self.data + data
    
    # verify this    
    def connectionLost(self, reason):
        # Add reconnect attempts!!!!
        log.msg("eat it jerky. USB connection lost for reason: %s" % reason)
        self.network.USBLost(reason)
        self.USB_connected = False
        # pass it up o the factory

# do a reactor stop?

class RFIDClient(LineReceiver):

    def connectionMade(self):
        log.msg('Connection received from tcp...')
        self.factory.client_list.append(self)

    def connectionLost(self, reason):
        log.msg('Connection lost because: %s' % reason)
        if self in self.factory.client_list:
            log.msg("Removing " + str(self))
            self.factory.client_list.remove(self)

    def lineReceived(self, line):
        log.msg('Command received: %s' % repr(line))
        self.factory.notifyAll(line)
        self.factory.notifyUSB(line)
        #Build command, if ok, send to serial port

# note, what about things going down to s port tho.

class RFIDClientFactory(Factory):
    protocol = RFIDClient

    def __init__(self):
        self.serial_port = None
        self.client_list = []

# notice that the log message below causes way too fucking much logging
    def notifyAll(self, data):
        for cli in self.client_list:
            log.msg("notify client: %s" % cli)
            cli.transport.write(data + '\r\n')

# when USB lost, notify the suckers and close out
    def USBLost(self, reason):
        self.serial_port = None
        self.notifyAll("USB Connection be lost: %s" % reason)
        from twisted.internet import reactor
        self.retry = reactor.callLater(5, self.establishConnection)        
        #self.dropAll()

# sending to s port now, it is ignoring us!!!!
    def notifyUSB(self, data):
        if self.serial_port:
            log.msg("send <%s> to s-port" % data)
            self.serial_port.write(data + '\r') # \n - nothin \r\n - sort of works. - \r is the key. Go figure!
    
    def dropAll(self):
        for cli in self.client_list:
            cli.transport.loseConnection()
            self.client_list.remove(cli)

    # retry?
    def establishConnection(self):
        # get reactor ref
        from twisted.internet import reactor
        try:
            log.msg("RFID Client Factory attempting to restore serial port conn")
            self.serial_port = SerialPort(USBClient(self), SERIAL_PORT, reactor, BAUD)
        except:
            log.msg("Error opening serial port %s (%s)" % (self.serial_port, sys.exc_info()[1]))
            log.msg("Reconnecting in 5 seconds...")
            self.retry = reactor.callLater(5, self.establishConnection)
            
"""

Below we set up the twistd DAEMON!

"""

SERIAL_PORT = '/dev/tty.usbmodem1a21'#'/dev/ttyUSB0'
BAUD = 57600

log.msg("Serial port be: %s" % SERIAL_PORT)
log.msg("Baud be: %s" % BAUD)

tcpfactory = RFIDClientFactory()

#   reactor.listenTCP(8000, tcpfactory)
# q remains: do we specify reactor for USB or something else?
# will blow up if you can't open the port, though
# so this is using the same factory, however other clients attaching to the server can't seem to see this!

# put this in a retry loop? For how long?

tcpfactory.establishConnection()
#sp = SerialPort(USBClient(tcpfactory), SERIAL_PORT, reactor, BAUD)
#tcpfactory.serial_port = sp



# service stuff
application = service.Application("rfid_network_server")
# note should do in settings.py
networkService = internet.TCPServer(6666, tcpfactory)
networkService.setServiceParent(application)
