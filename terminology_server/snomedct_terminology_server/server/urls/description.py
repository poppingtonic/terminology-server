from django.conf.urls import url

from . import views
from django.views.decorators.cache import cache_page
from snomedct_terminology_server.config.settings import CACHE_LIFETIME

description_urls = [
    url(r'descriptions/$',
        cache_page(CACHE_LIFETIME)(views.ListDescriptions.as_view()),
        name='list-descriptions'),

    url(r'description/(?P<id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.GetDescription.as_view()),
        name='get-description'),

    url(r'descriptions/concept_id/(?P<concept_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListDescriptionsForConcept.as_view()),
        name='get-descriptions-for-concept')
]
