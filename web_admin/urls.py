from django.conf.urls.defaults import patterns, include, url
from thermo.views import thermo_set
from django.contrib.auth.views import login

import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'BloomingLabs.views.home', name='home'),
    # url(r'^BloomingLabs/', include('BloomingLabs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^thermo/(?P<setting>.+)?', thermo_set),
    url(r'^accounts/login/$', login),
)
# SDC 12/20/2012
urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    
# final resort
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.WWW_ROOT,
            }),
)
