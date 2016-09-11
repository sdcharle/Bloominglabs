SAMPLE_TEXT = """Sensor Name   Last Event Alert Status    Configuration  
Motion Sensor  3 mins   no alert        No action set  
Front Door     52 mins   no alert        Alarm on opened
Toilet         2 mins   no alert        Alarm on dry   
"""

FIELD_LOOKUP = {
	"Motion Sensor":"LaserRoomMotion",
	"Front Door":"FrontDoor",
	"Back Door":"BackDoor",
	"Toilet": "Toilet",
	"Garage Door Sensor":"GarageDoorOpen",
	"Garage Door":"GarageDoorLocked",
	"Bathroom Door":"BathroomDoor",
	"Printrbot":"3DPrinter",
	"Entryway":"EntryWay",
	"Iron":"SolderingIrons",
	"Refrigerator":"Refrigerator",
	"Safe":"Safe",
	"Tool Shed":"Toolshed"
}

CHANNEL = "BloominglabsONE"

from beebotte import *
import subprocess
import re
import time
import sensitive

_token = sensitive.token
GET_DATA = '/home/blabs/hh/hh.pl'

def getText():
	return subprocess.check_output([GET_DATA])

if __name__ == '__main__':
	myBB = BBT(token = _token)
	while True:
		text = getText() # SAMPLE_TEXT
		#print text
		for ootline in text.split('\n')[1:-1]:
			fields = re.split('\s{2,}', ootline)
			if FIELD_LOOKUP.has_key(fields[0]):
				#print "looking at %s" % fields[0]
				times = fields[1].split(' ')
				try:
					if fields[2] == 'alarm triggered' or (times[1] == 'seconds' or (times[1] == 'mins' and int(times[0]) < 5)):
						#print "true"
						myBB.write(CHANNEL, FIELD_LOOKUP[fields[0]], True)
					else:
						#print "false"
						myBB.write(CHANNEL, FIELD_LOOKUP[fields[0]], False)
				except Exception:
					print "Technical difficulties. Wait a min and try again. %s" % Exception
					time.sleep(60)
		time.sleep(300) # 5 min
