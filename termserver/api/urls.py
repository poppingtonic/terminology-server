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
from .views import ConceptView


ENUMERATION_TYPES = {
    'root': 138875005,
    'is_a': 116680003,
    'core_metadata': 900000000000441003,
    'foundation_metadata': 900000000000454005,
    'reference_sets': 900000000000455006,
    'attributes': 246061005,
    'relationship_types': 410662002,
    'namespaces': 410662002,
    'navigational': 363743006,
    'module_identifiers': 900000000000443000,
    'definition_status_identifiers': 900000000000444006,
    'description_type_identifiers': 900000000000446008,
    'case_significance_identifiers': 900000000000447004,
    'characteristic_type_identifiers': 900000000000449001,
    'modifier_identifiers': 900000000000450001,
    'identifier_scheme_identifiers': 900000000000453004,
    'attribute_value_identifiers': 900000000000491004,
    'reference_set_descriptor_identifiers': 900000000000456007
}

urlpatterns = patterns(
    '',
    url(r'^concepts/(?P<concept_id>\d+)/(?P<representation_type>[a-z_A-Z]+)/$',
        ConceptView.as_view()),
    url(r'^concepts/(?P<concept_id>\d+)/$', ConceptView.as_view()),
)
