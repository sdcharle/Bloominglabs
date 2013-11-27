from django.conf.urls.defaults import patterns, include, url
import settings
from thermo.views import *
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
