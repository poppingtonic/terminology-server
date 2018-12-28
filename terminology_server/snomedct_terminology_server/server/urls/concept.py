from django.conf.urls import url

from . import views

concept_urls = [
    url(r'concepts/$',
        views.ListConcepts.as_view(),
        name='list-concepts'),

    url(r'concepts/metadata/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000441003},
        name='list-metadata-concepts'),

    url(r'concepts/metadata/core/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000442005},
        name='list-core-metadata-concepts'),

    url(r'concepts/metadata/foundation/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000454005},
        name='list-foundation-metadata-concepts'),

    url(r'concepts/refsets/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000455006},
        name='list-refset-concepts'),

    url(r'concepts/attributes/$',
        views.ListDescendants.as_view(),
        {'concept_id': 246061005},
        name='list-attribute-concepts'),

    url(r'concepts/reltypes/$',
        views.ListDescendants.as_view(),
        {'concept_id': 410662002},
        name='list-reltype-concepts'),

    url(r'concepts/namespaces/$',
        views.ListDescendants.as_view(),
        {'concept_id': 370136006},
        name='list-namespace-concepts'),

    url(r'concepts/top_level/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 138875005},
        name='list-top-level-concepts'),

    url(r'concept/root/$',
        views.GetConcept.as_view(),
        {'id': 138875005},
        name='get-root-concept'),

    url(r'concept/ancestry_graph/(?P<concept_id>\d+)/$',
        views.get_concept_ancestry_graph,
        name='get-concept-ancestry-graph'),

    url(r'concept/is_a/$',
        views.GetConcept.as_view(),
        {'id': 116680003},
        name='get-parent-child-concept'),

    url(r'concept/(?P<id>\d+)/$',
        views.GetConcept.as_view(),
        name='get-concept'),

    url(r'concept_list_by_id/$',
        views.get_concept_list_by_id,
        name='get-concept-preferred-term'),

    url(r'module_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000443000},
        name='list-module-identifiers'),

    url(r'definition_status_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000444006},
        name='list-definition-status-identifiers'),

    url(r'description_type_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000446008},
        name='list-description-type-identifiers'),

    url(r'case_significance_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000447004},
        name='list-case-significance-identifiers'),

    url(r'characteristic_type_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000449001},
        name='list-characteristic-type-identifiers'),

    url(r'modifier_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000450001},
        name='list-modifer-identifiers'),

    url(r'identifier_scheme_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000453004},
        name='list-identifier-scheme-identifiers'),

    url(r'attribute_value_identifiers/$',
        views.ListDescendants.as_view(),
        {'concept_id': 900000000000491004},
        name='list-attribute-value-identifiers'),

    url(r'reference_set_descriptor_identifiers/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 900000000000455006},
        name='list-reference-set-descriptor-identifiers')
]
