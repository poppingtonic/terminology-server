# coding=utf-8
"""URLs specific to the REST API"""
from rest_framework import routers

from .views import ConceptReadViewSet


router = routers.DefaultRouter()
#router.register(r'concepts', ConceptReadViewSet)

urlpatterns = router.urls
