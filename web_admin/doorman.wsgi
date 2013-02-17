import os
import sys
print "whiskey time"
sys.path.append('/home/access/Bloominglabs/')
sys.path.append('/home/access/Bloominglabs/web_admin')
sys.path.append('/home/access/Bloominglabs/web_admin/doorman')
os.environ['DJANGO_SETTINGS_MODULE'] = 'web_admin.settings'
print sys.path
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
print "no longer whiskey time"
