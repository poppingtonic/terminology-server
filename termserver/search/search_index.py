# coding=utf-8
"""Helper functions for ElasticSearch indexing"""
from core.models import ConceptDenormalizedView
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from django.core.paginator import Paginator
from django.conf import settings

from .search_utils import Timer
from .search_shared import INDEX_NAME, INDEX_BATCH_SIZE, MAPPING_TYPE_NAME, INDEX_SETTINGS
from .search_shared import extract_document

import logging
import django

LOGGER = logging.getLogger(__name__)


def bulk_index():
    """Resorted to using the ElasticSearch official driver in 'raw' form because ElasticUtils was a PITA"""
    # Get the elasticsearch instance
    es = Elasticsearch()

    # Drop the index, if it exists
    es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

    # Ignore 400 caused by IndexAlreadyExistsException when creating an index
    es.indices.create(
        index=INDEX_NAME,
        body=INDEX_SETTINGS,
        ignore=400,
        master_timeout=120, timeout=120  # Increased because of the need to set up synonyms
    )

    # Chunk concepts into chunks of 1000 for indexing ( balance memory and bulk index performance )
    concepts = ConceptDenormalizedView.objects.all()
    paginator = Paginator(concepts, INDEX_BATCH_SIZE)
    number_of_pages = paginator.num_pages
    LOGGER.debug("%d pages of %d records each" % (number_of_pages, INDEX_BATCH_SIZE))

    for page_number in paginator.page_range:
        with Timer() as t:
            page = paginator.page(page_number)
            documents = (
                extract_document(None, entry)
                for entry in page.object_list
            )
            doc_actions = (
                {
                    "_op_type": "index",
                    "_id": document["id"],
                    "_type": MAPPING_TYPE_NAME,
                    "_index": INDEX_NAME,
                    "_source": document
                } for document in documents
            )
            # Index in bulk, for performance reasons
            bulk(client=es, actions=doc_actions)

        # Clear cached queries to save memory when DEBUG = True
        if settings.DEBUG:
            django.db.reset_queries()

        # This helps when debugging performance issues
        LOGGER.debug(
            "Took %.03f seconds to index this batch ( of up to %d items ). This is page %d of %d" %
            (t.interval, INDEX_BATCH_SIZE, page_number, paginator.num_pages)
        )

    # Refresh the indexes
    es.indices.refresh(INDEX_NAME)



# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process; be sure to start Celery too
# TODO Implement API and perform sanity checks using UMLS UTS search engine; include full search API, esp. synonyms
# TODO Implement a dynamic snapshot view for all components
