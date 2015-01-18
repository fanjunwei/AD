from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
from wadmin.views import HomeView, uploadImage

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^wadmin/', include('wadmin.urls', namespace='wadmin')),
                       url(r'^uploadImage/$', uploadImage),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
