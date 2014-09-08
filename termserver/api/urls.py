# coding=utf-8
"""URLs specific to the REST API

There are specialized URLs for the following enumeration types:

    * `root` - display information about the root concept,
    including its direct / indirect children
    * `core_metadata` - a listing of core metadata concepts
    ( enumerated values applicable to core components )
    * `foundation_metadata` - a listing of foundation metadata concepts
    ( reference sets and their metadata )
    * `reference_sets` - a listing of known reference sets
    * `attributes` - a listing of attributes that may be applied to models
    * `relationship_types` - a listing of they valid relationship types
    e.g |is a|
    * `namespaces` - a listing of namespaces issued to organizations that
    can author terminologies
    * `navigational` - a listing of concepts whose role is purely
    navigational
    * `module_identifiers` - a listing of known modules
    * `definition_status_identifiers` - a listing of valid definition
    statuses
    * `description_type_identifiers` - a listing of valid description
    type identifiers
    * `case_significance_identifiers` - a listing of valid case
    significance identifiers
    * `characteristic_type_identifiers` - a listing of valid characteristic
    type identifiers
    * `modifier_identifiers` - a listing of valid modifiers
    * `identifier_scheme_identifiers` - a listing of valid identifier
    schemes
    * `attribute_value_identifiers` - a listing of valid attribute values
    * `reference_set_descriptor_identifiers` - a listing of valid reference
    set descriptors
"""
from django.conf.urls import patterns, url
from .views import ConceptView, SubsumptionView


urlpatterns = patterns(
    '',
    # Key concepts
    url(r'^concepts/(?P<concept_id>\d+)/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view()),
    url(r'^concepts/(?P<concept_id>\d+)/$', ConceptView.as_view()),

    url(r'^concepts/root/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 138875005}),
    url(r'^concepts/root/$', ConceptView.as_view(), {'concept_id': 138875005}),

    url(r'^concepts/is_a/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 116680003}),
    url(r'^concepts/is_a/$', ConceptView.as_view(), {'concept_id': 116680003}),

    url(r'^concepts/core_metadata/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000441003}),
    url(r'^concepts/core_metadata/$', ConceptView.as_view(),
        {'concept_id': 900000000000441003}),

    url(r'^concepts/foundation_metadata/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000454005}),
    url(r'^concepts/foundation_metadata/$', ConceptView.as_view(),
        {'concept_id': 900000000000454005}),

    url(r'^concepts/reference_set/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000455006}),
    url(r'^concepts/reference_set/$', ConceptView.as_view(),
        {'concept_id': 900000000000455006}),

    url(r'^concepts/attribute/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 246061005}),
    url(r'^concepts/attribute/$', ConceptView.as_view(),
        {'concept_id': 246061005}),

    url(r'^concepts/relationship_type/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 410662002}),
    url(r'^concepts/relationship_type/$', ConceptView.as_view(),
        {'concept_id': 410662002}),

    url(r'^concepts/namespace/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 370136006}),
    url(r'^concepts/namespace/$', ConceptView.as_view(),
        {'concept_id': 370136006}),

    url(r'^concepts/navigational/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 363743006}),
    url(r'^concepts/navigational/$', ConceptView.as_view(),
        {'concept_id': 363743006}),

    url(r'^concepts/module/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000443000}),
    url(r'^concepts/module/$', ConceptView.as_view(),
        {'concept_id': 900000000000443000}),

    url(r'^concepts/definition_status/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000444006}),
    url(r'^concepts/definition_status/$', ConceptView.as_view(),
        {'concept_id': 900000000000444006}),

    url(r'^concepts/description_type/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000446008}),
    url(r'^concepts/description_type/$', ConceptView.as_view(),
        {'concept_id': 900000000000446008}),

    url(r'^concepts/case_significance/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000447004}),
    url(r'^concepts/case_significance/$', ConceptView.as_view(),
        {'concept_id': 900000000000447004}),

    url(r'^concepts/characteristic_type/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000449001}),
    url(r'^concepts/characteristic_type/$', ConceptView.as_view(),
        {'concept_id': 900000000000449001}),

    url(r'^concepts/modifier/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000450001}),
    url(r'^concepts/modifier/$', ConceptView.as_view(),
        {'concept_id': 900000000000450001}),

    url(r'^concepts/identifier_scheme/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000453004}),
    url(r'^concepts/identifier_scheme/$', ConceptView.as_view(),
        {'concept_id': 900000000000453004}),

    url(r'^concepts/attribute_value/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view(), {'concept_id': 900000000000491004}),
    url(r'^concepts/attribute_value/$', ConceptView.as_view(),
        {'concept_id': 900000000000491004}),

    # Subsumption
    url(r'^subsumption/(?P<concept_id>[0-9]+)/$', SubsumptionView.as_view()),
)
