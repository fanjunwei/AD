# coding=utf-8
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Article(models.Model):
    user = models.ForeignKey(User, verbose_name=u'作者')
    title = models.CharField(max_length=255, verbose_name=u'标题')
    content = models.TextField(max_length=255, null=False, blank=True, verbose_name=u'内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'发表时间')