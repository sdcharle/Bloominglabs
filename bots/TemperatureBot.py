#!/usr/bin/env python
"""
11-17-2013 SDC
Grab temperature, humidity, and thermostat status from the 'web server' Arduino and report that shit to Xively.

To dos:
add logging and shit
frameworkize these xively bots son
"""

import time,re,sys
import urllib2
import logging
sys.path.append('/home/pi/Bloominglabs/web_admin')

from pachube_updater import *

logger = logging.getLogger('tempbot_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('tempbot.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("Happy daze the temperature bot started.")

SAMPLE_TEXT = """
<HTML>
<HEAD>
<meta name='apple-mobile-web-app-capable' content='yes' />
<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
<link rel='stylesheet' type='text/css' href='http://homeautocss.net84.net/a.css' />
<TITLE>Home Automation</TITLE>
</HEAD>
<BODY>
<br />
<h1>Humidity: 44.40 %	Temperature: 76.82 F
</h1>
<p>The Heat is:
OFF</p><a href="/?heaton"">Turn On Heat</a>
<a href="/?heatoff"">Turn Off Heat</a><br />
</BODY>
</HTML>
"""

TEMP_URL = "http://192.168.1.3"
temp_pat = re.compile(r'(\d+\.\d+).*?(\d+\.\d+)', re.MULTILINE)
thermo_pat = re.compile(r'(\w+)\<\/p\>\<a href="\/\?heat', re.MULTILINE)
pac = Pachube('/v2/feeds/53278.xml')
SLEEP_INTERVAL = 300 # do stuff every 5 minutes

def get_page(url):
    response = urllib2.urlopen(TEMP_URL)
    return response.read()

def parse_temp(temp_text):
    temp = None
    humidity = None
    thermostat = None
    
    m = temp_pat.search(temp_text)
    if m:
        temp = m.groups()[1]
        humidity = m.groups()[0]
    m = thermo_pat.search(temp_text)

    if m:
        thermostat = m.groups()[0]
        if thermostat == "ON":
            thermostat = 1
        else:
            thermostat = 0
    return (temp, humidity, thermostat)

def main():
    logger.info("Main loop in effect")
    while(True):
        temp = None
        humidity = None
        thermostat = None
        try:
            html = get_page(TEMP_URL)
            if html:
                (temp, humidity, thermostat) = parse_temp(html)
        except Exception, val:
            logger.error("While getting the Webpage we had exception [%s] with val [%s]" % (Exception, val))
        
        try:
            if temp:
                pac.log('Temperature', temp)
            if humidity:
                pac.log('Humidity', humidity)
            if thermostat is not None:
                pac.log('Thermostat', thermostat)
        except Exception, val:
            logger.error("While posting to Xively we had exception [%s] with val [%s]" % (Exception, val))
        time.sleep(SLEEP_INTERVAL)

if __name__ == '__main__':
    main()

