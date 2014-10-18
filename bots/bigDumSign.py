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

DATABASE_FILE = "SignQueue.db"
    
class SignQueue:
    def __init__(self,databaseFile = DATABASE_FILE):
        self.conn = conn = sqlite3.connect(databaseFile)
        conn.row_factory = sqlite3.Row

    def addMessage(self, message, start_time, life_time, priority):
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
    while True:
        SQ.cleanQueue()
        r = SQ.pullMessage()
        if r:
            print r['message']
        time.sleep(10)


if __name__ == '__main__':
    main()
    
    
"""

1 3
2 2
3 2
4 3

msgs come out in order

prio then id
1 3
4 3
2 2
3 2

1
4
1
4
(does not loop back from 4 to 2!)

want
highest
then next highest
etc
then loop
(rowcount????)


get all results and walk thru?

is_active


"""