# coding=utf-8
"""URLs specific to the REST API"""
from django.conf.urls import patterns, url

from .views import (
    ConceptView,
    SubsumptionView,
    DescriptionView,
    RelationshipView,
    RefsetView,
    AdminView
)

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

    # Concept list and detail views
    url(r'^concepts/$', ConceptView.as_view({'get': 'list'})),
    url(
        r'^concepts/(?P<concept_id>\d+)/(?P<representation_type>\w+)/$',
        CONCEPT_RETRIEVAL_VIEW, name='concept-detail-extended'
    ),
    url(
        r'^concepts/(?P<concept_id>\d+)/$',
        CONCEPT_RETRIEVAL_VIEW, name='concept-detail-short'
    ),

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
        RelationshipView.as_view({'get': 'list'})),

    # Reference set detail view ( view single items )
    url(r'^refset/detail/(?P<refset_id>[0-9]+)/(?P<entry_id>[-\w]+)/$',
        RefsetView.as_view({'get': 'retrieve'}), name='refset-detail'),

    # General purpose reference set list views
    url(r'^refset/(?P<refset_id>[0-9]+)/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'})),
    url(r'^refset/(?P<refset_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'})),

    # Simple reference sets
    url(r'^refset/simple/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 446609009}),
    url(r'^refset/simple/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 446609009}),

    # Ordered reference sets
    url(r'^refset/ordered/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 447258008}),
    url(r'^refset/ordered/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 447258008}),

    # Attribute value reference sets
    url(r'^refset/attribute_value/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000480006}),
    url(r'^refset/attribute_value/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000480006}),

    # Simple map reference sets
    url(r'^refset/simple_map/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000496009}),
    url(r'^refset/simple_map/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000496009}),

    # Complex map reference sets
    url(r'^refset/complex_map/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 447250001}),
    url(r'^refset/complex_map/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 447250001}),

    # Extended map reference sets
    url(r'^refset/extended_map/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 609331003}),
    url(r'^refset/extended_map/$',
        RefsetView.as_view({'get': 'list'}), {'refset_id': 609331003}),

    # Language reference sets
    url(r'^refset/language/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000506000}),
    url(r'^refset/language/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000506000}),

    # Query specification reference sets
    url(r'^refset/query_specification/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000512005}),
    url(r'^refset/query_specification/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000512005}),

    # Annotation reference sets
    url(r'^refset/annotation/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000516008}),
    url(r'^refset/annotation/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000516008}),

    # Association reference sets
    url(r'^refset/association/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000521006}),
    url(r'^refset/association/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000521006}),

    # Module dependency reference sets
    url(r'^refset/module_dependency/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000534007}),
    url(r'^refset/module_dependency/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000534007}),

    # Description format reference sets
    url(r'^refset/description_format/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000538005}),
    url(r'^refset/description_format/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000538005}),

    # Reference set descriptor reference sets
    url(r'^refset/reference_set_descriptor/(?P<module_id>[0-9]+)/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000456007}),
    url(r'^refset/reference_set_descriptor/$',
        RefsetView.as_view({'get': 'list'}),
        {'refset_id': 900000000000456007}),

    # Admin URLs
    url(r'^admin/namespace/$', AdminView.as_view({'get': 'namespace'})),
    url(r'^admin/releases/$', AdminView.as_view({'get': 'releases'})),
)
