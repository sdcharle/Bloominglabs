"""
Ever-so-basic Twisted + SQLite tests
SDC 8/8/88, I mean 8/8/12

use testdb database
users table
name
update_time
sync_time
syncing

http://stackoverflow.com/questions/8578531/getting-data-from-simple-select-using-twisted-enterprise-adbapi/8579061#8579061
http://twistedmatrix.com/documents/current/core/howto/rdbms.html
http://twistedmatrix.com/documents/12.0.0/api/twisted.enterprise.adbapi.Transaction.html
http://stackoverflow.com/questions/11534882/transaction-support-in-twisted-adbapi

1) looping call
2) TimedService

  def interaction(txn):
      x = doSql(txn, "select thingy from foo where bar = baz;")
      doSql(txn, "update foo set thingy = ? where bar = baz;", x+1)
  cp.runInteraction(interaction)

http://twistedmatrix.com/documents/current/core/examples/#auto5
http://twistedmatrix.com/documents/current/core/howto/rdbms.html


this appears to be a good ref re: db stuff
http://www.mail-archive.com/twisted-python@twistedmatrix.com/msg01101.html



General rules:
look for: update > sync time but not syncing. Update (set to 'syncing'). Also (eventually) send the command to do an update to da firmware
when you hear from the firmware - compare record to what's in DB. Set update time to now and syncing to 0 if it's good.

That's pretty much it, really. Add a piece to cover deletes (put shit in a delete queue)

Add a check to ensure shit is synced.

Ignore anything w/ mask = 255

note, yes twisted is some K-razee shit!
Why do you think they call it twisted?

Other 'app notes'
bogus tag values goin' to arduino end up being mapped to 0
fun fact from A Martelli:
If you want, for example, the value corresponding to the smallest key, thedict[min(thedict)] will do that.

weird, keeps coming back as 'invalid'


8/15/2012

8/20/2012
handle tag case diffs

various observations:
store tags always as uc (do comparisons that way)
Mods to Ard-side code (clean up comms)
Better Auth (clients have to auth to server. lock down USB port)

keep track of slot/userid distinctions


--- sync proc basics are good!

Next steps:

print -> debug
sync in loop
restrict sync check to ones w/ slot specified (that's the check)
check 'unauthorized' against the database schedule
get timezones right.

8/21/2012
User delete queue (Django side)

note, this is a better way to fetch as dictionary:
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

still trouble w/ slots
need:
slot is unique BUT user can have null (no slot) 

Ultimately will just have to handle slots under the covers, this is gettin' hairy.

handle...
0:0:0  0/0/0  User deleted at position 1

"""

import sqlite3
from datetime import datetime, timedelta
import sys
import shlex # better (simpler) line splits on whitespace etc.
import re

# twisted imports
from twisted.internet.task import LoopingCall
from twisted.enterprise import adbapi
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log

SERIAL_PORT = '/dev/tty.usbmodem1d11' #"/dev/tty.usbmodem1a21" # <- left port on mac. right port -> '/dev/tty.usbmodem1d11'
BAUD = 57600

class USBClient(LineReceiver): #Protocol):
      
    def __init__(self, userDB):
        # note, shit like this pattern should be class-level
        self.userPattern = re.compile("\d+\s+\d+\s+(\d|[ABCDEF])+$")        
        self.lastCommand = ""        
        self.successStack = []
        self.updateStack = {} # because slot is important
        self.userDB = userDB
        def echo(line):
            log.msg("From USB:%s" % line )
        self.receiveHandler = echo # anything popping in on line receive will call this.
        self.authenticated = False
        self.password = "99bead00"

    def authenticate(self):
        log.msg("Authenticate....")
        self.transport.write("e %s\r" % self.password)
 
    # note, using slot 'coz have to for Arduino.
    # so just adding a user to 24 hour won't work, need to add a slot.
    # btw, this slot mgmt biz could get ugly (could do under the covers though, that's the most user friendly.)
    def fillUpdateStack(self,rows):
        print 'hey amigo, got results'
        for row in rows:
            print row
            self.updateStack[str(row[3])] =  {"mask":str(row[1]), "tag":row[2], "processing":0, "user_id":row[0]}
        for k in self.updateStack.keys():
            print "%s: %s" % (k, self.updateStack[k])
        
        # kick off the update sequence
        self.processStack()
            
    # if stuff on the stack, get to sending.
    def processStack(self):
        if self.updateStack:
            for k in self.updateStack.keys():
                if self.updateStack[k]["processing"] == 0:
                    item = self.updateStack[k]
                    item["processing"] = 1
                    self.sendLine("m %s %s %s" % (k,item["mask"], item["tag"]))
                    return # ugh. drop out after first!
        print "Nothing in stack. Gonna hang out."
        
    # wipes anything NOT in the Django db, loads the DB (better future approach - ban direct command line type access)
    # note, are we guaranteed no stomping?
    def wipeAndSync(self):
        self.updateStack = {}
        for i in range(200):
            # add one per
            self.updateStack[str(i)] = {"mask":"255", "tag":"FFFFFFFF", "processing":0}
        user_db.getAllUsers().addCallbacks(self.fillUpdateStack,self.userDB.operationError)
                          
    def connectionFailed(self):
        log.msg( "USB Connection Failed:" + repr(self))
        reactor.stop()

# what to do when successful.
# handle the case of mask down doesn't = mask up.
    def handleSuccess(self,line):
        log.msg("Received succeed line:%s" % line)

        (user,mask,tag) = shlex.split(line)
        if user in self.successStack:
            if self.updateStack[user]["mask"] == mask and upper(self.updateStack[user]["tag"]) == upper(tag):
                print "ok looks good"
            else:
                print "update failed. was: %s" % self.updateStack[user]
            user_id = self.updateStack[user]['user_id']
            
            # experiments (clean up later)
            def itsGood(result):
                log.msg("sync interaction is done.")
            # mark it good at DB level:
            def wordUp(txn):
                self.userDB.markUserSynced(txn, user_id)
                log.msg("Marked as sync succeeded")
                self.successStack.remove(user)
                del self.updateStack[user]
                self.processStack()
            self.userDB.runInteraction(wordUp).addCallbacks(itsGood)         
            return
        raise Exception("Oh shit wtf")
        
    def connectionMade(self):
        log.msg('Connected to USB port')

    def prepareForSuccess(self,line):
        self.successStack.append(shlex.split(line)[3])
        log.msg("will look for user %s to succeed" % self.successStack[-1])
        
    # this one could use some polishing. if-then ad infinitum is icky
    # note also - getting 'invalid command' a LOT. Sending too many new lines?
    def lineReceived(self, line):        
        log.msg("USB Line received: %s" % repr(line))
        
        if self.userPattern.search(line) and self.successStack:
            self.handleSuccess(line)
            return  
        # is it a 'user modified' type line?
        
        if line.find("Access Denied. Priveleged mode is not enabled") > -1:
            
            self.authenticate()
            return # ?
        
        if line.find("Priveleged mode enabled.") > -1:
            log.msg("you are authenticated")
            self.authenticated = True
            if self.last_command:
                self.sendLine(self.last_command)
                self.lastCommand = ""
            return
            
        if line.find("rebooted") > -1:
            #self.wipeAndSync()
            # don't do this in general. (Special util?)
            # looks like a sep of powers issue below.
            d = self.userDB.runInteraction(self.userDB.getUserToSync)
            d.addCallbacks(self.fillUpdateStack, self.userDB.operationError)

            return
        # add as command at srvr level
        
        if line.find("successfully modified") > -1:    
            self.prepareForSuccess(line)
            return
        self.receiveHandler(line)
        #self.network.notifyAll(line)
        # err, not yourself, though.

    def sendLine(self, command):
        log.msg("Command sent down: %s" % command)
        self.transport.write(str(command + "\r")) # note if you try to send unicode down it yakks
        self.last_command = command

    def outReceived(self, data):
        log.msg("outReceived! with %d bytes!" % len(data))
        self.data = self.data + data
    
    # verify this    
    def connectionLost(self, reason):
        log.msg("eat it jerky. USB connection lost for reason: %s" % reason)
        self.network.USBLost(reason)

# following this pattern is wise
# see: http://cutter.rexx.com/~dkuhlman/twisted_patterns.html#the-database-update-pattern

# SDC, should things be all contained w/in trans at this level? I'm thinking the answer is yes

class UserDatabase(adbapi.ConnectionPool): 
    """
    Update and retrieve from the User database.
    """ 

    def getAllUsers(self):
        print 'get all users'
        return self.runQuery("SELECT user_id, rfid_access, rfid_tag, rfid_slot from doorman_userprofile")

    def getChangedUsers(self):
        print 'lookin for users changed or new'
        return self.runQuery("SELECT user_id, rfid_access, rfid_tag, rfid_slot from doorman_userprofile " + \
                               "WHERE (sync_date is null)  or (update_date > sync_date) and syncing = 0")
    
    def getUserToSync(self,txn):
# adding/deleting handled in Django i/f - this is some limited db interaction - even if sync flag is checked, pick up stuff > 10 min old, something's wrong
        print "let's sync users"
        sql="SELECT user_id, rfid_access, rfid_tag, rfid_slot from doorman_userprofile " + \
                                 "WHERE ((sync_date is null)  or (update_date > sync_date)) " + \
                                 " and (syncing = 0 or update_date < datetime('now','-10 minute')) limit 1"
        ten_min_ago = datetime.now() + timedelta(minutes = -10)
        txn.execute(sql,(ten_min_ago,))
        result=txn.fetchall()
        if result:
            print "yo chuck we got to do updates:"
            for r in result:
                print r[0]
            # now update that shit
            sql = "update doorman_userprofile set syncing = 1 where user_id = ?"

            txn.execute(sql,(result[0][0],))
        else:
            print "no updates, keep on keepin' on"
        return result
    
    def markUserSynced(self,txn, user_id):
        print "user is synced, we cool"
        now = datetime.now()
        sql = "update doorman_userprofile set sync_date = ?, syncing = 0 where user_id = ?"
        txn.execute(sql,(now,user_id,))
        
    def syncLoop(self):
        self.runInteraction(self.setUsersSyncing).addCallbacks(happy_day, self.operationError)
        
    def operationError(self, error):
        log.err(error)
        print "%s Operation Failed: %s" % (self.__class__, error)

# this is dopey
def happy_day(ignore):
    print "success, yay woo!"

def big_query_result_dump(result):
    print "interaction result: %s" % result

if __name__ == '__main__':
    
    log.startLogging(sys.stdout) # file('app.log', 'w'))
    
    log.msg("Serial port be: %s" % SERIAL_PORT)
    log.msg("Baud be: %s" % BAUD)
    
    from twisted.internet import reactor
    user_db = UserDatabase("sqlite3", '/Users/scharlesworth/BloomingLabs/web_admin/BloomingLabs.db')
    uc = USBClient(user_db)
    sp = SerialPort(uc, SERIAL_PORT, reactor, BAUD)
    print 'connection is bangin'
 
# put this shit in a loop   
#    d = user_db.runInteraction(user_db.setUsersSyncing)
#    d.addCallbacks(happy_day,user_db.operationError)
    
    #lc = LoopingCall(user_db.syncLoop) #.addCallbacks(happy_day,user_db.operationError))
    #lc.start(2)
    # timeout, when, func
    #reactor.callLater(1,uc.wipeAndSync)
# get an error for above:
#exceptions.AttributeError: Deferred instance has no __call__ method
    print 'initiate reactor' 
    reactor.run() 