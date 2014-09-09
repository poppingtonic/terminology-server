# coding=utf-8
"""URLs specific to the REST API"""
from django.conf.urls import patterns, url

from .views import ConceptView
from .views import SubsumptionView
from .views import DescriptionView
from .views import RelationshipView

CONCEPT_RETRIEVAL_VIEW = ConceptView.as_view({'get': 'retrieve'})

urlpatterns = patterns(
    '',
    # Key concepts
    url(r'^concepts/(?P<concept_id>\d+)/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW),
    url(r'^concepts/(?P<concept_id>\d+)/$', CONCEPT_RETRIEVAL_VIEW),

    url(r'^concepts/root/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 138875005}),
    url(r'^concepts/root/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 138875005}),

    url(r'^concepts/is_a/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 116680003}),
    url(r'^concepts/is_a/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 116680003}),

    url(r'^concepts/core_metadata/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000441003}),
    url(r'^concepts/core_metadata/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000441003}),

    url(r'^concepts/foundation_metadata/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000454005}),
    url(r'^concepts/foundation_metadata/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000454005}),

    url(r'^concepts/reference_set/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000455006}),
    url(r'^concepts/reference_set/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000455006}),

    url(r'^concepts/attribute/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 246061005}),
    url(r'^concepts/attribute/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 246061005}),

    url(r'^concepts/relationship_type/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 410662002}),
    url(r'^concepts/relationship_type/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 410662002}),

    url(r'^concepts/namespace/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 370136006}),
    url(r'^concepts/namespace/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 370136006}),

    url(r'^concepts/navigational/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 363743006}),
    url(r'^concepts/navigational/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 363743006}),

    url(r'^concepts/module/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000443000}),
    url(r'^concepts/module/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000443000}),

    url(r'^concepts/definition_status/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000444006}),
    url(r'^concepts/definition_status/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000444006}),

    url(r'^concepts/description_type/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000446008}),
    url(r'^concepts/description_type/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000446008}),

    url(r'^concepts/case_significance/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000447004}),
    url(r'^concepts/case_significance/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000447004}),

    url(r'^concepts/characteristic_type/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000449001}),
    url(r'^concepts/characteristic_type/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000449001}),

    url(r'^concepts/modifier/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000450001}),
    url(r'^concepts/modifier/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000450001}),

    url(r'^concepts/identifier_scheme/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000453004}),
    url(r'^concepts/identifier_scheme/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000453004}),

    url(r'^concepts/attribute_value/(?P<representation_type>[a-z_A-Z]+)/$',
        CONCEPT_RETRIEVAL_VIEW, {'concept_id': 900000000000491004}),
    url(r'^concepts/attribute_value/$', CONCEPT_RETRIEVAL_VIEW,
        {'concept_id': 900000000000491004}),

    # Concept list
    url(r'^concepts/$', ConceptView.as_view({'get': 'list'})),

    # Subsumption
    url(r'^subsumption/(?P<concept_id>[0-9]+)/$',
        SubsumptionView.as_view({'get': 'retrieve'})),

    # Descriptions
    url(r'^descriptions/(?P<component_id>[0-9]+)/$',
        DescriptionView.as_view({'get': 'retrieve'})),
    url(r'^descriptions/$',
        DescriptionView.as_view({'get': 'list'})),

    # Relationships
    url(r'^relationships/(?P<component_id>[0-9]+)/$',
        RelationshipView.as_view({'get': 'retrieve'})),
    url(r'^relationships/$',
        RelationshipView.as_view({'get': 'list'}))
)
