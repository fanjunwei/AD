# coding=utf-8
# Date: 14/11/21
# Time: 09:11
# Email:fanjunwei003@163.com
from django.conf.urls import patterns, url
from views import *

__author__ = u'范俊伟'

urlpatterns = patterns('wadmin',
                       url(r'^img_code/$', get_img_code, name='img_code'),
                       url(r'^register/$', RegisterView.as_view(), name='register'),
                       url(r'^login/$', LoginView.as_view(), name='login'),
                       url(r'^logout/$', logout, name='logout'),
                       url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
                       url(r'^test_ad/$', TestADView.as_view(), name='test_ad'),
                       url(r'^send_article/$', SendArticleView.as_view(), name='send_article'),
                       url(r'^article/(?P<id>\d*?)$', ArticleView.as_view(), name='article'),
)
