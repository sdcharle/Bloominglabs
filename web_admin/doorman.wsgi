import os
import sys
sys.path.append('/home/pi/Bloominglabs/')
sys.path.append('/home/pi/Bloominglabs/web_admin')
sys.path.append('/home/pi/Bloominglabs/web_admin/doorman')
sys.path.append('/home/pi/Bloominglabs/web_admin/thermo')
os.environ['DJANGO_SETTINGS_MODULE'] = 'web_admin.settings'
print sys.path
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
