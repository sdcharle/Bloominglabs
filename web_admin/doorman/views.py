import rfid_sock
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import local_settings

@login_required(login_url='/wsgi-scripts/accounts/login/')
def open_door(request):
    success =  rfid_sock.open_fucking_door(local_settings.RFID_PASSWORD,
        local_settings.RFID_HOST, 
    	local_settings.RFID_PORT) 
    return render_to_response('door_open.html',
                              { "success":success })
