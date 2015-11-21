# Create your views here.
import rfid_sock

@login_required(login_url='/wsgi-scripts/accounts/login/')
def open_door(request, setting):
    success =  rfid_sock.open_fucking_door(local_settings.RFID_HOST, 
    	local_settings.RFID_PORT, 
    	local_settings.RFID_PASSWORD)
    return render_to_response('door_open.html',
                              { "success":success })