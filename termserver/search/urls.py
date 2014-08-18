# coding=utf-8
"""Wire up search related APIs"""
from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns(
    '',
    url(r'(?P<search_type>[a-zA-Z]+)/$', views.SearchView.as_view()),
)
