from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^wadmin/', include('wadmin.urls', namespace='wadmin')),
)
