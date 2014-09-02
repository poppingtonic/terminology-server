# coding=utf-8
"""Wire up search related APIs"""
from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns(
    '',
    url(r'(?P<search_type>[a-zA-Z]+)/(?P<shortcut_type>[a-z_A-Z]+)/$',
        views.SearchView.as_view()),
    url(r'(?P<search_type>[a-zA-Z]+)/$', views.SearchView.as_view()),
)
