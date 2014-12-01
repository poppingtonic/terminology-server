# coding=utf-8
"""The project / main URL configuration; imports from app URL configs"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^docs/', include('rest_framework_swagger.urls', namespace='docs')),
    url(r'^terminology/', include('api.urls', namespace='terminology')),
    url(r'^search/', include('search.urls', namespace='search')),
)
