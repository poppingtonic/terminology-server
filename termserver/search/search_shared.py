# coding=utf-8
"""
Classes and modules that are shared between indexing and searching

A deliberate choice has been made to index only the information that is relevant to search. The rest of the information
will always be a single ( fast ) SQL query away. We rely upon the fact the ElasticSearch transparently indexes lists -
the reason why there is no "special treatment" for "descriptions".

The "preferred_term" and "fully_specified_name" are stored in the index - because they are commonly used in rendering,
and it is beneficial to be able to render them without an additional database query. The "parents" and "children"
fields concern themselves only with the subsumption ( "is a" ) relationship. This is by far the most frequently
interrogated relationship.
"""
from core.models import ConceptView
from django.conf import settings

import os

# We only plan to have one index, one type; so these can be constants
INDEX_NAME = 'concept-index'
INDEX_BATCH_SIZE = 10000
MAPPING_TYPE_NAME = 'concept'
SNOMED_STOPWORDS = [
    'ABOUT', 'ALONGSID', 'AN', 'AND', 'ANYTHING', 'AROUND', 'AS', 'AT', 'BECAUSE', 'BEFORE', 'BEING', 'BOTH', 'BY',
    'CANNOT', 'CHRONICA', 'CONSISTS', 'COVERED', 'DOES', 'DURING', 'EVERY', 'FINDS', 'FOR', 'FROM', 'IN', 'INSTEAD',
    'INTO', 'MORE', 'MUST', 'NO', 'NOT', 'OF', 'ON', 'ONLY', 'OR', 'PROPERLY', 'SIDE', 'SIDED', 'SOME', 'SOMETHIN',
    'SPECIFIC', 'THAN', 'THAT', 'THE', 'THINGS', 'THIS', 'THROUGHO', 'TO', 'UP', 'USING', 'USUALLY', 'WHEN', 'WHILE',
    'WITHOUT'
]
SYNONYMS_FILE_NAME = settings.BASE_DIR + "/synonyms.txt"
WORD_EQUIVALENTS_PATH = os.path.dirname(settings.BASE_DIR) + \
    "/terminology_data/zres_WordEquivalents_en-US_INT_20020731.txt"
MAPPING = {
    'dynamic': 'strict',
    'properties': {
        # The main identifier, to be used to look up the concept when more detail is needed
        # It is stored but not analyzed
        'id': {
            'type': 'long',
            'index': 'no',  # Not searchable; because the primary key is not meaningful
            'coerce': False,  # We are strict
            'store': True  # Store each field so that we can retrieve directly
        },
        'concept_id': {
            'type': 'long',
            'index': 'analyzed',
            'coerce': False,
            'store': True,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        # The next group of properties will be used for filtering
        # They are stored but not analyzed
        'active': {
            'type': 'boolean',
            'store': True
        },
        'is_primitive': {
            'type': 'boolean',
            'store': True
        },
        'module_id': {
            'type': 'long',
            'index': 'analyzed',
            'store': True,
            'coerce': False,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        'module_name': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        # The primary "human identifiers" of a concept; stored but not analyzed
        'fully_specified_name': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        'preferred_term': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        # Indexed string ( array ) fields
        # These fields are analyzed ( searchable ); the default search field should be "descriptions"
        'descriptions': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        'descriptions_autocomplete': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'autocomplete',
            'search_analyzer': 'standard_with_stopwords'
        },
        # Relationship fields - used solely for filtering; only the target concept_ids are stored
        # Stored but not analyzed
        'parents': {
            'type': 'long',
            'index': 'analyzed',
            'store': True,
            'coerce': False,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        },
        'children': {
            'type': 'long',
            'index': 'analyzed',
            'store': True,
            'coerce': False,
            'index_analyzer': 'standard_with_stopwords',
            'search_analyzer': 'standard_with_stopwords'
        }
    }
}
INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 5,
        "number_of_replicas": 1,
        "index.mapping.ignore_malformed": False,
        "index.mapping.coerce": False,
        "index.mapper.dynamic": False,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 20
                },
                "synonym": {
                    "type": "synonym",
                    "synonyms_path": SYNONYMS_FILE_NAME
                }
            },
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "standard",
                        "lowercase",
                        "stop",
                        "autocomplete_filter"
                    ]
                },
                "standard_with_stopwords": {
                    "type": "standard",
                    "stopwords": SNOMED_STOPWORDS
                },
                "synonyms": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "standard",
                        "lowercase",
                        "stop",
                        "synonym"
                    ]
                }
            }
        }
    },
    "mappings": {
        MAPPING_TYPE_NAME: MAPPING
    }
}


# Helper methods

def extract_document(obj_id, obj=None):
    """A helper method that turns a ConceptView record into an indexable document
    :param obj_id:
    """
    if not obj:
        obj = ConceptView.objects.filter(id=obj_id)[0]

    # This is used twice; compute and cache
    descriptions = list(set([item["term"] for item in obj.descriptions_list]))

    return {
        'id': obj.id,
        'concept_id': obj.concept_id,
        'active': obj.active,
        'is_primitive': obj.is_primitive,
        'module_id': obj.module_id,
        'module_name': obj.module_name,
        'fully_specified_name': obj.fully_specified_name,
        'preferred_term': obj.preferred_term,
        'descriptions': descriptions,
        'descriptions_autocomplete': descriptions,
        'descriptions_snowball': descriptions,
        'parents': list(set([rel["concept_id"] for rel in obj.is_a_parents])),
        'children': list(set([rel["concept_id"] for rel in obj.is_a_children]))
    }
