# coding=utf-8
"""URLs specific to the REST API"""
from django.conf.urls import patterns, url, include
from rest_framework import routers

from .views import ConceptReadViewSet


router = routers.DefaultRouter()
router.register(r'concepts', ConceptReadViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
