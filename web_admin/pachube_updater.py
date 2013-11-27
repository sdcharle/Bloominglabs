#!/usr/bin/env python
"""
SDC 12/22/2011 Merry XMAS to you!
SDC 1/14/2012 Testing w/ ATTiny85 sensor - removed temp (shitty readings anyway)
SDC 3/24/2012
for the bloominglabs feeds.

Could try official API, too:
https://pachube.com/docs/v2/datastream/update.html

"""
import eeml
import eeml.datastream
import datetime
# blabs specific key
API_KEY = '<GIT YR OWN FOOL>'
# for Pachube
OnOffUnit = eeml.Unit('On/Off', 'basicSI', 'ON')

class PachubeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Pachube():
    def __init__(self,url, key = API_KEY):
        # changed since pachube is now Cosm 
        self.pac = eeml.datastream.Cosm(url, API_KEY)

    def log(self,datastream_name, value, unit = OnOffUnit):
        try:
            self.pac.update([
                    eeml.Data(datastream_name, value, unit = unit)
                    ])
            self.pac.put()
        except Exception, value:
            raise PachubeError("%s:%s" % (Exception,value))
        
if __name__ == '__main__':
    pac = Pachube('/v2/feeds/53278.xml')
    #print pac.log(1, 100, OnOffUnit)
    print pac.log('Door', 0, OnOffUnit)
    print pac.log('Office',0,OnOffUnit)
    print pac.log('Workshop',1,OnOffUnit)
