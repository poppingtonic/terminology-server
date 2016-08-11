from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

description_urls = [
    url(r'descriptions/$',
        views.ListDescriptions.as_view(),
        name='list-descriptions'),

    url(r'description/(?P<id>\d+)/$',
        views.GetDescription.as_view(),
        name='get-description'),

    url(r'descriptions/concept_id/(?P<concept_id>\d+)/$',
        views.ListDescriptionsForConcept.as_view(),
        name='get-descriptions-for-concept')
]
