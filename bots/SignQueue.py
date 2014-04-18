"""

Some sign fun including:

schedule messages for later
specify message life
message priority - higher is 'higher'

Just do it in SQLite?
yes.

CREATE TABLE "sign_queue" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "message" varchar(140) NOT NULL, 
    "start_time" datetime NOT NULL,
    "life_time" integer not null default 60,
    "priority" integer not null default 1,
    "add_time" datetime NOT NULL,
    "is_active" integer default 0
);

SDC 4/2/2014

"""
import logging
from datetime import datetime
import sqlite3
import sys
import time


LOG_FILENAME = 'signQueue.log'
logger = logging.getLogger(sys.argv[0])
logger.setLevel(logging.INFO)
file_log = logging.FileHandler(LOG_FILENAME,'a')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s")
file_log.setFormatter(formatter)
logger.addHandler(file_log)
# add console, too!
import simplejson as sj

DATABASE_FILE = "SignQueue.db"


class SignMessage:
    def __init__(self, message, start_time=None, life_time = 60, priority = 1):
        if not start_time:
            start_time = datetime.now()
        
        self.dict = {"message":message, "start_time":str(start_time), "life_time":life_time, "priority":priority}
        self.json = sj.dumps(self.dict)
    
class SignQueue:
    def __init__(self,databaseFile = DATABASE_FILE):
        self.conn = conn = sqlite3.connect(databaseFile)
        conn.row_factory = sqlite3.Row

    def addMessage(self, message, start_time=None, life_time = 60, priority = 1):
        
        #hacky wacky
        try:
            print "dict"
            
            if type(message) is dict:
            #    message = message.dict
                print "start time"
                if message.has_key("start_time"):
                    start_time = message["start_time"]
                print "life_time"
                if message.has_key("life_time"):
                    life_time = message["life_time"]
                print "priority"
                if message.has_key("priority"):
                    priority = message["priority"]
                print "message"
                if message.has_key("message"):
                    print "has key"
                    message = message["message"]
                else:
                    message = None
        except Exception, val:
            print "add message is not sign queue type:(%s, %s)" % (Exception, val)
            pass
        
        if not message:
            return # nothing to do
        
        if not start_time:
            start_time = datetime.now()
        try:
            self.conn.execute("insert into sign_queue (message, start_time, life_time, priority, add_time) values (?,?,?,?, datetime('now'))",(message, start_time, life_time, priority))
            self.conn.commit()
        except Exception, val:
            self.conn.rollback()
            logger.error("fuck up in queue insert: %s, %s" % (Exception, val))
 
    def purgeQueue(self):
        self.conn.execute("truncate table sign_queue")
        self.conn.commit()
        
    # get: next message w/ highest priority that's not 'active'
    # but cycle thru or you are in bad shape
    
    def pullMessage(self):
        self.cleanQueue()
        result = None
        cur = self.conn.cursor()
        # add condition s.t. higher priority jumps the line! this doesn't get it if lower id has higher priority though!
        cur.execute("""
                    select id, message, start_time, life_time, priority from sign_queue where is_active = 0 and
                    id > (select id from sign_queue where is_active = 1) order by priority desc, id asc;""")
        r = cur.fetchone()
        if not r: # loop back around. not super efficient but what you gonna do
            cur.execute('select id, message, start_time, life_time, priority from sign_queue where is_active = 0 order by priority desc, id asc;')
            r = cur.fetchone()
        if r:
            print r
            result = r
            cur.close()
            self.conn.execute('update sign_queue set is_active = 0 where is_active = 1')
            self.conn.execute('update sign_queue set is_active = 1 where id = ?', (int(r['id']),))
            self.conn.commit()

        return result
        
    # any message past it's life time, fuck it, delete it.
    def cleanQueue(self):
        self.conn.execute("delete from sign_queue where strftime('%s',datetime(current_timestamp,'localtime')) - strftime('%s', datetime(start_time)) > life_time;")
        self.conn.commit()    
    

def main():
    SQ = SignQueue()
    SQ.addMessage('welcome to highland lounge!', datetime.now(), 60,1)
    SQ.addMessage('Home of Joe Mama\'s Pizza!', datetime.now(), 120,1)
    SQ.addMessage('Now 50% meth-free!', datetime.now(), 120,1)
    SM = SignMessage("dingy wingy", datetime.now(), 70, 1)
    print SM.json
    print SM.dict
    SQ.addMessage(SM)
    
    while True:
        r = SQ.pullMessage()
        if r:
            print r['message']
        time.sleep(10)


if __name__ == '__main__':
    main()
    
