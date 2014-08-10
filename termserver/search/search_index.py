# coding=utf-8
"""Helper functions for ElasticSearch indexing"""
from core.models import ConceptView
from elasticsearch.helpers import bulk
from django.core.paginator import Paginator
from django.conf import settings

from .search_utils import Timer
from .search_shared import ConceptMapping, INDEX_NAME, INDEX_BATCH_SIZE, MAPPING_TYPE_NAME

import logging
import django

LOGGER = logging.getLogger(__name__)

"""
A deliberate choice has been made to index only the information that is relevant to search. The rest of the information
will always be a single ( fast ) SQL query away. We rely upon the fact the ElasticSearch transparently indexes lists -
the reason why there is no "special treatment" for "descriptions".

The "preferred_term" and "fully_specified_name" are stored in the index - because they are commonly used in rendering,
and it is beneficial to be able to render them without an additional database query. The "parents" and "children"
fields concern themselves only with the subsumption ( "is a" ) relationship. This is by far the most frequently
interrogated relationship.
"""
INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 5,
        "number_of_replicas": 1,
        "index.mapping.ignore_malformed": False,
        "index.mapping.coerce": False,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 20
                }
            },
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter"
                    ]
                }
            }
        }
    }
}
MAPPING = {
    'properties': {
        # The main identifier, to be used to look up the concept when more detail is needed
        # It is stored but not analyzed
        'concept_id': {
            'type': 'long',
            'index': 'no',  # Not searchable; because SCTIDs are not meaningful
            'coerce': False,  # We are strict
            'store': True  # Store each field so that we can retrieve directly
        },
        # The next group of properties will be used for filtering
        # They are stored but not analyzed
        'active': {
            'type': 'boolean',
            'index': 'no',  # Indexing boolean fields is close to useless
            'store': True
        },
        'is_primitive': {
            'type': 'boolean',
            'index': 'no',
            'store': True
        },
        'module_id': {
            'type': 'long',
            'index': 'no',
            'store': True,
            'coerce': False
        },
        'module_name': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        # The primary "human identifiers" of a concept; stored but not analyzed
        'fully_specified_name': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        'preferred_term': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        # Indexed string ( array ) fields
        # These fields are analyzed ( searchable ); the default search field should be "descriptions"
        'descriptions': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        'descriptions_autocomplete': {
            'type': 'string',
            'index': 'analyzed',
            'store': True,
            'index_analyzer': 'autocomplete',
            'search_analyzer': 'standard'
        },
        # Relationship fields - used solely for filtering; only the target concept_ids are stored
        # Stored but not analyzed
        'parents': {
            'type': 'long',
            'index': 'no',
            'store': True,
            'coerce': False
        },
        'children': {
            'type': 'long',
            'index': 'no',
            'store': True,
            'coerce': False
        }
    }
}

# Helper methods


def _extract_document(obj_id, obj=None):
    """A helper method that turns a ConceptView record into an indexable document"""
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
        'parents': list(set([rel["concept_id"] for rel in obj.is_a_parents])),
        'children': list(set([rel["concept_id"] for rel in obj.is_a_children]))
    }


def bulk_index():
    """Resorted to using the ElasticSearch official driver in 'raw' form because ElasticUtils was a PITA"""
    # Get the elasticsearch instance
    es = ConceptMapping.get_es()

    # Drop the index, if it exists
    es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

    # Ignore 400 caused by IndexAlreadyExistsException when creating an index
    es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS, ignore=400)

    # Chunk concepts into chunks of 1000 for indexing ( balance memory and bulk index performance )
    concepts = ConceptView.objects.all()
    paginator = Paginator(concepts, INDEX_BATCH_SIZE)
    number_of_pages = paginator.num_pages
    LOGGER.debug("%d pages of %d records each" % (number_of_pages, INDEX_BATCH_SIZE))

    for page_number in paginator.page_range:
        with Timer() as t:
            page = paginator.page(page_number)
            documents = (
                _extract_document(None, entry)
                for entry in page.object_list
            )
            doc_actions = (
                {
                    "_op_type": "index",
                    "_id": document["id"],
                    "_type": MAPPING_TYPE_NAME,
                    "_index": INDEX_NAME,
                    "doc": document
                } for document in documents
            )
            # Index in bulk, for performance reasons
            bulk(client=es, actions=doc_actions, stats_only=False)

        # Clear cached queries to save memory when DEBUG = True
        if settings.DEBUG:
            django.db.reset_queries()

        # This helps when debugging performance issues
        LOGGER.debug(
            "Took %.03f seconds to index this batch ( of up to %d items ). This is page %d of %d" %
            (t.interval, INDEX_BATCH_SIZE, page_number, paginator.num_pages)
        )

    # Refresh the indexes
    es.indices.refresh(ConceptMapping.get_index())


# TODO For tests, use from elasticutils.contrib.django.estestcase import ESTestCase and default ES_DISABLED to True, turning it on selectively when needed
# TODO Use a unique index name for tests, so that tests do not clobber the production database

# TODO Synonyms - process SNOMED word equivalents into synonyms
# TODO Create custom analyzer for synonyms and set it up as the query time analyzer
# TODO "full" queries: use a **common terms query** with the "and" operator for low frequency and "or" operator for high frequency; index analyzer to standard
# TODO Add query template, with support for filtering by parents, children, module, primitive, active
# TODO Ensure that synonym support can be turned on/off via query parameter
# TODO Incorporate phrase suggester into all searches
# TODO Incorporate "more like this" into all searches; easy - see below; pass it the search object
# s = S().filter(product='firefox')
# mlt = MLT(2034, s=s)

# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process; be sure to start Celery too
# TODO Fix process around downloading, preparing and updating UK release content
# TODO Implement API and perform sanity checks on concepts using UMLS UTS search engine
# TODO Implement pep8 checks in tests
# TODO Fix test coverage issues
