# coding=utf-8
"""Helper functions for search"""
from elasticsearch import Elasticsearch
from .search_shared import INDEX_NAME, MAPPING_TYPE_NAME


def search(query_string='', active=None, primitive=None, module_ids=None, parents=None, children=None,
           include_synonyms=True, verbose=True, query_type='full'):
    """
    Wrap the raw Elasticsearch operations

    :rtype : list
    :param query_string: string derived from user input ( assumed to be sanitized )
    :param active: one of [True], [False], [True,False] or [False,True]
    :param primitive: one of [True], [False], [True,False] or [False,True]
    :param module_ids: list of longs ( SCTIDs )
    :param parents: list of longs ( SCTIDs )
    :param children: list of longs ( SCTIDs )
    :param include_synonyms: True or False
    :param verbose: True or False
    :param query_type: one of 'full' ( default ) or 'autocomplete'
    """
    query_analyzer = 'synonyms' if include_synonyms else 'standard'
    query_field = 'descriptions_autocomplete' if query_type == 'autocomplete' else 'descriptions'
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
    query_body = {
        "query": {
            "filtered": {
                "query": {
                    "match": {
                        query_field: {
                            "query": query_string,
                            "analyzer": query_analyzer,
                            "cutoff_frequency": 0.01,
                            "fuzziness": "AUTO"
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
    query_fields = 'concept_id,active,is_primitive,module_id,module_name,fully_specified_name,preferred_term'
    return Elasticsearch().search(
        index=INDEX_NAME,  # The name of the index that is to be searched
        doc_type=MAPPING_TYPE_NAME,  # The name of the document type that is to be searched
        body=query_body,  # Elasticsearch query DSL ( dict )
        analyzer=query_analyzer,  # The query string analyzer can be switched out at runtime
        analyze_wildcard=False,  # Whether to process wildcard and prefix queries
        _source=verbose,  # Whether to include the raw source with each query result
        fields=query_fields,  # The fields to return as a part of the result
        explain=verbose,  # Whether to provide an explanation for each query
        lenient=False,  # Do not process malformed queries
        allow_no_indices=False,  # Do not process if a wildcard expression does not resolve into a concrete index
        lowercase_expanded_terms=True,  # Normalize all query terms to lower case
        size=30,  # Return up to 30 results; no pagination, no "next"
        suggest_field='descriptions',  # Base suggestions on the combined descriptions field
        suggest_size=12,  # Return up to 12 suggestions
        suggest_text=query_string,  # Return suggestions based on the supplied query string
        timeout=5,  # This is not even sufficiently aggressive; searches should be very fast
        version=True  # Return the document version as a part of the hit
    )