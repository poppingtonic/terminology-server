# coding=utf-8
"""Helper functions for search"""
from elasticsearch import Elasticsearch
from .search_shared import INDEX_NAME, MAPPING_TYPE_NAME


def search(
        query_string='', active=[True], primitive=[False],
        module_ids=None, parents=None, children=None,
        include_synonyms=True, verbose=True, refsets=None,
        query_type='full'):
    """
    Wrap the raw Elasticsearch operations

    :rtype : list
    :param query_string: string derived from user input ( assumed sanitized )
    :param active: one of [True], [False], [True,False] or [False,True]
    :param primitive: one of [True], [False], [True,False] or [False,True]
    :param module_ids: list of longs ( SCTIDs )
    :param parents: list of longs ( SCTIDs )
    :param children: list of longs ( SCTIDs )
    :param include_synonyms: True or False
    :param verbose: True or False
    :param refsets: a list of SCTIDs of refsets; supply if you wish to
    confine the search to the concepts that are referred to from those refsets
    :param query_type: one of 'full' ( default ) or 'autocomplete'
    """
    query_analyzer = 'synonyms' if include_synonyms else 'standard'
    query_field = 'descriptions_autocomplete' if query_type == 'autocomplete' \
        else 'descriptions'
    query_filters = []
    if active is not None:
        query_filters.append({"terms": {"active": active}})
    if primitive is not None:
        query_filters.append({"terms": {"is_primitive": primitive}})
    if module_ids:
        query_filters.append({"terms": {"module_id": module_ids}})
    if parents:
        query_filters.append({"terms": {"parents": parents}})
    if children:
        query_filters.append({"terms": {"children": children}})
    if refsets:
        query_filters.append({"terms": {"refsets": refsets}})
    query_body = {
        "query": {
            "filtered": {
                "query": {
                    "match": {
                        query_field: {
                            "query": query_string,
                            "analyzer": query_analyzer
                        }
                    }
                },
                "filter": {
                    "bool": {
                        "must": query_filters
                    }
                }
            }
        }
    }
    query_fields = 'concept_id,active,is_primitive,module_id,module_name,'
    'fully_specified_name,preferred_term,parents,children,refsets'
    return Elasticsearch(timeout=300).search(
        index=INDEX_NAME,  # The name of the index that is to be searched
        doc_type=MAPPING_TYPE_NAME,  # The document type that is to be searched
        body=query_body,  # Elasticsearch query DSL ( dict )
        analyzer=query_analyzer,  # Can be switched out at runtime
        analyze_wildcard=False,  # Whether to process wildcard & prefix queries
        _source=verbose,  # Whether to include the raw source with each result
        fields=query_fields,  # The fields to return as a part of the result
        explain=verbose,  # Whether to provide an explanation for each query
        lenient=False,  # Do not process malformed queries
        allow_no_indices=False,  # Abort if a wildcard doesnt resolve
        lowercase_expanded_terms=True,  # Normalize all terms to lower case
        size=30,  # Return up to 30 results; no pagination, no "next"
        suggest_field='descriptions',  # Use the combined descriptions field
        suggest_size=12,  # Return up to 12 suggestions
        suggest_text=query_string,  # Suggest using the supplied query string
        version=True  # Return the document version as a part of the hit
    )
