# coding=utf-8
"""Helper functions for ElasticSearch indexing"""
from core.models import ConceptView
from elasticsearch.helpers import bulk
from django.core.paginator import Paginator
from django.conf import settings

from .search_utils import Timer
from .search_shared import ConceptMapping, INDEX_NAME, INDEX_BATCH_SIZE, MAPPING_TYPE_NAME, INDEX_SETTINGS
from .search_shared import _extract_document

import logging
import django

LOGGER = logging.getLogger(__name__)


def bulk_index():
    """Resorted to using the ElasticSearch official driver in 'raw' form because ElasticUtils was a PITA"""
    # Get the elasticsearch instance
    es = ConceptMapping.get_es()

    # Drop the index, if it exists
    es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

    # Ignore 400 caused by IndexAlreadyExistsException when creating an index
    es.indices.create(
        index=INDEX_NAME,
        body=INDEX_SETTINGS,
        ignore=400
    )

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
                    "_id": document["concept"]["id"],
                    "_type": MAPPING_TYPE_NAME,
                    "_index": INDEX_NAME,
                    MAPPING_TYPE_NAME : document
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
