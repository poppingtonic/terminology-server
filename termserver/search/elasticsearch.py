# coding=utf-8
"""Set up ElasticSearch indexing and search"""
from core.models import ConceptView
from elasticutils.contrib.django import MappingType, Indexable
from django.conf import settings
from .utils import Timer

import logging
import django

LOGGER = logging.getLogger(__name__)

# We only plan to have one index, one type; so these can be constants
INDEX_NAME = 'concept-index'
MAPPING_TYPE_NAME = 'concept'

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
        # Unique identifier, to be used to look up the concept when more detail is needed
        # It is stored but not analyzed
        'concept_id': {
            'type': 'long',
            'index': 'no',  # Not searchable; because SCTIDs are not meaningful
            'coerce': False  # We are strict
        },
        # The next group of properties will be used for filtering
        # They are stored but not analyzed
        'active': {
            'type': 'boolean',
            'index': 'no'  # Indexing boolean fields is close to useless
        },
        'is_primitive': {
            'type': 'boolean',
            'index': 'no'
        },
        'module_id': {
            'type': 'long',
            'index': 'no',
            'coerce': False
        },
        'module_name': {
            'type': 'string',
            'index': 'analyzed',
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        # The primary "human identifiers" of a concept; stored but not analyzed
        'fully_specified_name': {
            'type': 'string',
            'index': 'analyzed',
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        'preferred_term': {
            'type': 'string',
            'index': 'analyzed',
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        # Indexed string ( array ) fields
        # These fields are analyzed ( searchable ); the default search field should be "descriptions"
        'descriptions': {
            'type': 'string',
            'index': 'analyzed',
            'index_analyzer': 'standard',
            'search_analyzer': 'standard'
        },
        'descriptions_autocomplete': {
            'type': 'string',
            'index': 'analyzed',
            'index_analyzer': 'autocomplete',
            'search_analyzer': 'standard'
        },
        # Relationship fields - used solely for filtering; only the target concept_ids are stored
        # Stored but not analyzed
        'parents': {
            'type': 'long',
            'index': 'no',
            'coerce': False
        },
        'children': {
            'type': 'long',
            'index': 'no',
            'coerce': False
        }
    }
}

# Helper methods


def _extract_document(obj_id):
    """A helper method that turns a ConceptView record into an indexable document"""
    obj = ConceptView.objects.filter(id=obj_id)[0]

    return {
        'id': obj.id,
        'concept_id': obj.concept_id,
        'active': obj.active,
        'is_primitive': obj.is_primitive,
        'module_id': obj.module_id,
        'module_name': obj.module_name,
        'fully_specified_name': obj.fully_specified_name,
        'preferred_term': obj.preferred_term,
        'descriptions': list(set([item["term"] for item in obj.descriptions_list])),
        'parents': list(set([rel["concept_id"] for rel in obj.is_a_parents])),
        'children': list(set([rel["concept_id"] for rel in obj.is_a_children]))
    }


def _chunk(list, n=1000):
    """ Yield successive n-sized chunks from l"""
    for i in xrange(0, len(list), n):
        yield list[i:i + n]


class ConceptMapping(MappingType, Indexable):
    """
    This mapping class is a thin wrapper around module level constants / functions

    Reason - the indexing uses "raw" elasticsearch-py; but needs to share code with the search implementation that uses
    this mapping. Why use "raw" elasticsearch-py? Because ElasticUtils support for indexing is a pain in the neck.
    """

    @classmethod
    def get_index(cls):
        """Explicitly set the index name, so that we can add other index types in future with minimal disruption"""
        return INDEX_NAME

    @classmethod
    def get_mapping_type_name(cls):
        """Name of the concept type in the search index"""
        return MAPPING_TYPE_NAME

    @classmethod
    def get_model(cls):
        """The mapping will use the materialized view"""
        return ConceptView

    @classmethod
    def get_mapping(cls):
        """Create an ElasticSearch mapping for Concept search"""
        return MAPPING

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """Convert the model instance into a searchable document"""
        return _extract_document(obj_id)


def bulk_index():
    """Resorted to using the ElasticSearch official driver in 'raw' form because ElasticUtils was a PITA"""
    # Get the elasticsearch instance
    es = ConceptMapping.get_es()

    # Drop the index, if it exists
    es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

    # Ignore 400 caused by IndexAlreadyExistsException when creating an index
    es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS, ignore=400)

    # Get all the concept IDs
    concept_ids = ConceptView.objects.all().values_list('id', flat=True)

    # Chunk it into chunks of 1000 IDs or less ( 1000 is the default size )
    concept_id_chunks = _chunk(concept_ids)

    # Index the chunks one at a time and refresh the index each time
    for concept_id_chunk in concept_id_chunks:
        try:
            with Timer() as t:
                documents = (_extract_document(con_id) for con_id in concept_id_chunk)
                for document in documents:
                    es.index(
                        index=INDEX_NAME,
                        doc_type=MAPPING_TYPE_NAME,
                        body=document,
                        id=document["id"],
                        refresh=False
                    )
        finally:
            # Clear cached queries to save memory when DEBUG = True
            if settings.DEBUG:
                django.db.reset_queries()
            LOGGER.debug("Took %.03f seconds to index this batch ( of up to 1000 items )" % t.interval)

    # Refresh the indexes
    es.indices.refresh(ConceptMapping.get_index())


def search():
    """Wrap the raw Elasticsearch operations"""
    searcher = ConceptMapping.search()
    # TODO Ensure that all queries have 25 items as default item number

# TODO For tests, use from elasticutils.contrib.django.estestcase import ESTestCase and default ES_DISABLED to True, turning it on selectively when needed
# TODO Use a unique index name for tests, so that tests do not clobber the production database

# TODO Synonyms - process SNOMED word equivalents into synonyms
# TODO Create custom analyzer for synonyms and set it up as the query time analyzer
# TODO "full" queries: use a **common terms query** with the "and" operator for low frequency and "or" operator for high frequency; index analyzer to standard
# TODO Add autocomplete field to mapping; edge-ngram, 3-20 characters
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
