from django.conf.urls import patterns, include, url

from django.contrib import admin
from wadmin.views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^wadmin/', include('wadmin.urls', namespace='wadmin')),
)
