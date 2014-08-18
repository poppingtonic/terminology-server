# coding=utf-8
"""The project / main URL configuration; imports from app specific URL configs"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^search/', include('search.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
)
