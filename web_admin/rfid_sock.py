#!/usr/bin/env python
 
import socket
import sys
import select
import re


HOST = 'localhost'
PORT = 6666
newpat =  re.compile("Tag: (\S+) successfully added with mask:(\S+)", re.M)
foundpat = re.compile("Tag: (\S+) found and updated to mask:(\S+)", re.M)

# do:
# returns True/False
# tested and works with
# no ard conn (times out, false)
# good update
# no network server present
# other test cases(?????)


def open_fucking_door(password, host = HOST, port = PORT):
    try:
      print "make socket"
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
      sys.stderr.write("[CREATE SOCKET ERROR] %s\n" % msg[1])
      return False
    try:
      print "connect"
      sock.connect((host,int(port)))
    except socket.error, msg:
      sys.stderr.write("[CONNECT ERROR] %s\n" % msg[1])
      return False
# add Exception below
    try:
        print "send"
        sock.send("o 1$%s\r\n" % (password))
    except socket.error, msg:
        sys.stderr.write("[SEND ERROR] %s\n" % msg[1])
        return False
    # at this point essentially fuck it.
    return True

def modify_user(host, port, tag, mask, password):
    try:
      print "make socket"
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
      sys.stderr.write("[CREATE SOCKET ERROR] %s\n" % msg[1])
      return False
    try:
      print "connect"
      sock.connect((host,port))
    except socket.error, msg:
      sys.stderr.write("[CONNECT ERROR] %s\n" % msg[1])
      return False
# add Exception below
    try:
        print "send"
        sock.send("m %s %s$%s\r\n" % (tag, mask, password))
    except socket.error, msg:
        sys.stderr.write("[SEND ERROR] %s\n" % msg[1])
        return False
    string = ""
    success = False
    print "read"
    while 1:
        rlist, wlist, elist = select.select( [sock,], [], [], 5 )
    
        # Test for timeout
        if [rlist, wlist, elist] == [ [], [], [] ]:
            print "Five seconds elapsed.\n"
            break
        else:
            data = sock.recv(1024)
            string = string + data
            match = foundpat.search(string)
            if match:
                print "tag: %s mask %s\n" % (match.group(1), match.group(2))
                success = True
                break;
            match = newpat.search(string)
            if match:
                print "tag: %s mask %s\n" % (match.group(1), match.group(2))
                success = True
                break

    print string
    print success
    return success

# wow, that's easy
# modify to look for a response(?)
def send_command(command):
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
      sys.stderr.write("[ERROR] %s\n" % msg[1])
      return None
    try:
      sock.connect((HOST, PORT))
    except socket.error, msg:
      sys.stderr.write("[ERROR] %s\n" % msg[1])
      return None
    
    sock.send(command )

    string = ""
    
    while 1:
        rlist, wlist, elist = select.select( [sock,], [], [], 5 )
    
        # Test for timeout
        if [rlist, wlist, elist] == [ [], [], [] ]:
            print "Five seconds elapsed.\n"
            break
        else:
            data = sock.recv(1024)
            string = string + data
            print "select read:%s" % data
    sock.close()     
    print string
    return string

if __name__ == '__main__':
    #send_command("m 222222 1$notpassword\r\n")
    modify_user(HOST, PORT, "222222", "1", "notpassword")
    sys.exit(0)
