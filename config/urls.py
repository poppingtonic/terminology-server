# coding=utf-8
"""The project / main URL configuration; imports from app URL configs"""
from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^terminology/', include('core.urls', namespace='terminology')),
)
