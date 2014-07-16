# coding=utf-8
"""URLs specific to the REST API"""
from rest_framework import routers

from .views import ReleaseInformationViewSet


router = routers.DefaultRouter()
router.register(r'version', ReleaseInformationViewSet)

urlpatterns = router.urls

