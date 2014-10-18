#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
"""
Basic client for the 'sign server'

periodically does a thing

"""

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from SignQueue import SignMessage

import sys

class SignClient(LineReceiver):
    counter = 0
    
    def connectionMade(self):
        self.sendLine('{"message":"Hello World"}')
        self.looper = LoopingCall(self.spitMessage)
        self.looper.start(5) # every 5


    def spitMessage(self):
        message = '{"message":"counter be: %s"}' % SignClient.counter
        SignClient.counter = SignClient.counter + 1
        self.sendLine(message)

    def lineReceived(self, line):
        print "receive:", line
        if line==self.end:
            self.transport.loseConnection()

class SignClientFactory(ClientFactory):
    protocol = SignClient

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    factory = SignClientFactory()
    reactor.connectTCP('localhost', 6666, factory)
    reactor.run()

if __name__ == '__main__':
    main()