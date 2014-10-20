# coding=utf-8
"""Helper functions for ElasticSearch indexing"""
from core.models import ConceptDenormalizedView
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from django.core.paginator import Paginator
from django.conf import settings

from .search_shared import INDEX_NAME, INDEX_BATCH_SIZE
from .search_shared import MAPPING_TYPE_NAME, INDEX_SETTINGS
from .search_shared import extract_document

import logging
import multiprocessing
import django

LOGGER = logging.getLogger(__name__)
MULTIPROCESSING_POOL_SIZE = multiprocessing.cpu_count()


# Get the elasticsearch instance
es = Elasticsearch()


def pool_initializer():
    LOGGER.debug('Starting %s' % multiprocessing.current_process().name)


def extract_page_documents(paginator, page_number):
    """A worker method that composes ready-to-index docs in bulk format"""
    page = paginator.page(page_number)
    documents = (
        extract_document(None, entry)
        for entry in page.object_list
    )
    return (
        {
            "_op_type": "index",
            "_id": document["id"],
            "_type": MAPPING_TYPE_NAME,
            "_index": INDEX_NAME,
            "_source": document
        } for document in documents
    )


def index_shard(doc_actions):
    """A worker that allows the actual calls to ES to be parallelized"""
    # Index in bulk, for performance reasons
    bulk(client=es, actions=doc_actions)

    # Clear cached queries to save memory when DEBUG = True
    if settings.DEBUG:
        django.db.reset_queries()


def bulk_index():
    """Using the ElasticSearch official driver in raw form for more control"""
    # Drop the index, if it exists
    es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

    # Ignore 400 caused by IndexAlreadyExistsException when creating an index
    es.indices.create(
        index=INDEX_NAME,
        body=INDEX_SETTINGS,
        ignore=400,
        master_timeout=120,
        timeout=120  # Increased because of the need to set up synonyms
    )

    # Chunk concepts into chunks of 10000 for indexing
    concepts = ConceptDenormalizedView.objects.all()
    paginator = Paginator(concepts, INDEX_BATCH_SIZE)
    no_of_pages = paginator.num_pages

    LOGGER.debug("%d pages, %d records each" % (no_of_pages, INDEX_BATCH_SIZE))

    # Index in parallel ( sending to ElasticSearch )
    shards = (
        extract_page_documents(paginator, page_number)
        for page_number in paginator.page_range
    )
    index_pool = multiprocessing.Pool(
        processes=MULTIPROCESSING_POOL_SIZE,
        initializer=pool_initializer,
        maxtasksperchild=15
    )
    index_pool_outputs = index_pool.map(index_shard, shards)
    index_pool.close()  # There will be no more tasks added
    index_pool.join()  # Wait for the processes to finish their work

    LOGGER.debug('Index pool outputs: %s' % index_pool_outputs)

    # Refresh the indexes
    es.indices.refresh(INDEX_NAME)



# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process; be sure to start Celery too
