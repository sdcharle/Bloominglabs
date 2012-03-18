#!/usr/bin/env python
"""

Super easy pushingbox API, because pushingbox is nice and easy

SDC 3/15/2012

"""

import  urllib , urllib2 
class pushingbox() :
    url = "" 
    def  __init__( self , devid, data ) :
        url = 'http://api.pushingbox.com/pushingbox'
        values = dict({'devid':devid}.items() + data.items())
        try:
            data = urllib.urlencode( values) 
            req = urllib2.Request ( url, data )
            stuff = urllib2.urlopen( req )
        except  Exception , detail:
            print  "Error" , detail
            
            
if __name__ == '__main__':
    key = "v3F858C5D9D81B83" 
    pushingbox(key, {'user':'rod of course'})