"""URLs config for base API

Find the component-specific urls in 'concept', 'relationship', and
'description' in this module.
"""

from django.conf.urls import url
from .. import views

from ..serializers import REFSET_MODELS
from snomedct_terminology_server.server.views import (
    generate_refset_list_view,
    generate_refset_detail_view,
    generate_refset_module_list_view)

from .concept import concept_urls
from .relationship import relationship_urls
from .description import description_urls

urlpatterns = [
    url(r'version/current/$',
        views.current_release_information,
        name='current-snomedct-release'),

    url(r'versions/$',
        views.historical_release_information,
        name='historical-releases')
]

refset_list_urls = [
    url(r"^refset/{}/$".format(refset_type.lower()),
        generate_refset_list_view(refset_model).as_view(),
        name="list-{}-refset".format(
            refset_type.lower().replace('_', '-')))
    for refset_type, refset_model in REFSET_MODELS.items()]

refset_detail_urls = [
    url(r"^refset/detail/{}/(?P<id>[-\w]+)/$".format(refset_type.lower()),
        generate_refset_detail_view(refset_model).as_view(),
        name="get-{}-refset-detail".format(
            refset_type.lower().replace('_', '-')))
    for refset_type, refset_model in REFSET_MODELS.items()]

refset_module_list_urls = [
    url(r"^refset/{}/(?P<module_id>[-\w]+)/$".format(refset_type.lower()),
        generate_refset_module_list_view(refset_model).as_view(),
        name="list-{}-refset-by-module".format(
            refset_type.lower().replace('_', '-')))
    for refset_type, refset_model
    in REFSET_MODELS.items()]

urlpatterns += concept_urls
urlpatterns += relationship_urls
urlpatterns += description_urls
urlpatterns += refset_list_urls
urlpatterns += refset_detail_urls
urlpatterns += refset_module_list_urls
