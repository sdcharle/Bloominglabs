
import time
import tweepy
import sys
from datetime import datetime
import subprocess
# keep ten records, if record 0 was less than

def talk(msg):
    p = subprocess.Popen("echo ' %s' | festival --tts" % msg, shell=True, stdout=subprocess.PIPE)

if __name__ == '__main__':
    while True:
        fred = raw_input()
	talk(fred) 
