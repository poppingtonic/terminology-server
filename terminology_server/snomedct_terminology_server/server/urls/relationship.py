from django.conf.urls import url
from django.views.decorators.cache import cache_page
from snomedct_terminology_server.config.settings import CACHE_LIFETIME
from . import views

relationship_urls = [
    url(r'relationship/(?P<id>\d+)/$',
        views.get_relationship,
        name='get-relationship'),

    url(r'relationships/$',
        cache_page(CACHE_LIFETIME)(views.ListRelationships.as_view()),
        name='list-relationships'),

    url(r'relationships/source/(?P<source_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListRelationships.as_view()),
        name='list-source-relationships'),

    url(r'relationships/defining/(?P<concept_id>\d+)/$',
        views.ListDefiningRelationships.as_view(),
        name='list-defining-relationships'),

    url(r'relationships/qualifying/(?P<concept_id>\d+)/$',
        views.ListAllowableQualifiers.as_view(),
        name='list-allowable-qualifiers'),

    url(r'relationship/parents/(?P<concept_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectParents.as_view()),
        name='list-concept-parents'),

    url(r'relationship/children/(?P<concept_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        name='list-concept-children'),

    url(r'relationship/ancestors/(?P<concept_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListAncestors.as_view()),
        name='list-concept-ancestors'),

    url(r'relationship/descendants/(?P<concept_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        name='list-concept-descendants'),

    url(r'relationships/destination/(?P<destination_id>\d+)/$',
        cache_page(CACHE_LIFETIME)(views.ListRelationships.as_view()),
        name='list-destination-relationships'),

    url(r'relationships/destination_by_type_id/(?P<type_id>\d+)/$',
        views.get_relationship_destination_by_type_id,
        name='list-destination-ids-by-type-id'),

    url(r'relationships/transitive_closure/$',
        views.TransitiveClosureList.as_view(),
        name='list-transitive-closure'),

    url(r'relationships/transitive_closure/adjacency_list/$',
        views.get_adjacency_list,
        name='adjacency-list'),

    url(r'relationships/transitive_closure_ancestors/(?P<subtype_id>\d+)/$',
        views.transitive_closure_ancestors,
        name='list-transitive-closure-ancestors'),

    url(r'relationships/transitive_closure_descendants/(?P<supertype_id>\d+)/$',
        views.transitive_closure_descendants,
        name='list-transitive-closure-descendants')
]
