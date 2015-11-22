from django.shortcuts import render_to_response
import urllib2, re
from django.contrib.auth.decorators import login_required

temp_pat = re.compile(r'(\d+\.\d+).*?(\d+\.\d+)', re.MULTILINE)
thermo_pat = re.compile(r'(\w+)\<\/p\>\<a href="\/\?heat', re.MULTILINE)

from local_settings import ARDUINO_URL

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

def get_page(url):
    response = urllib2.urlopen(url)
    return response.read()

@login_required(login_url='/wsgi-scripts/accounts/login/')
def thermo_set(request, setting):
    url =  ARDUINO_URL

    temp = None
    humidity = None
    thermostat = None
    
    if setting == "ON":
        url += "/?heaton"
    elif setting == "OFF":
        url += "/?heatoff"    
    try:
        html = get_page(url)
        if html:
            (temp, humidity, thermostat) = parse_temp(html)
    except Exception, val:
        print "oh fucksticks: %s - %s" % (Exception, val)
    return render_to_response('thermo_set.html',
                              { 'temp': temp,
                               'humidity': humidity,
                               'thermostat': thermostat})
