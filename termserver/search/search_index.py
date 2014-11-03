# coding=utf-8
"""Helper functions for ElasticSearch indexing"""
import logging
import multiprocessing

from core.models import SearchContentView
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from django.core.paginator import Paginator
from django.db import connection

from .search_shared import INDEX_NAME, INDEX_BATCH_SIZE
from .search_shared import MAPPING_TYPE_NAME, INDEX_SETTINGS

LOGGER = logging.getLogger(__name__)
MULTIPROCESSING_POOL_SIZE = multiprocessing.cpu_count()


# Get the elasticsearch instance


def pool_initializer():
    """Called upon the start of each process in the multiprocessing pool"""
    LOGGER.debug('Starting %s' % multiprocessing.current_process().name)


def extract_page_documents(page_number):
    """A worker method that composes ready-to-index docs in bulk format"""
    page = Paginator(
        SearchContentView.objects.all(), INDEX_BATCH_SIZE
    ).page(page_number)
    doc_actions = (
        {
            "_op_type": "index",
            "_id": document["id"],
            "_type": MAPPING_TYPE_NAME,
            "_index": INDEX_NAME,
            "_source": document
        } for document in (
            {
                'id': entry.id,
                'concept_id': entry.concept_id,
                'concept_name': entry.concept_name,
                'active': entry.active,
                'is_primitive': entry.is_primitive,
                'module_id': entry.module_id,
                'module_name': entry.module_name,
                'fully_specified_name': entry.fully_specified_name,
                'preferred_term': entry.preferred_term,
                'descriptions': entry.descriptions,
                'descriptions_autocomplete': entry.descriptions,
                'parents': entry.is_a_parent_ids,
                'children': entry.is_a_children_ids
            }
            for entry in page.object_list
        )
    )

    # Index in bulk, for performance reasons
    bulk(client=Elasticsearch(timeout=300), actions=doc_actions)


def bulk_index():
    """Using the ElasticSearch official driver in raw form for more control"""
    # Get a connection to ElasticSearch

    es = Elasticsearch(timeout=300)
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

    concepts = SearchContentView.objects.all()
    paginator = Paginator(concepts, INDEX_BATCH_SIZE)
    no_of_pages = paginator.num_pages
    LOGGER.debug("%d pages, %d records each" % (no_of_pages, INDEX_BATCH_SIZE))

    # Index in parallel ( sending to ElasticSearch )
    connection.close()  # Let each child process open its own connection
    shard_pool = multiprocessing.Pool(
        processes=MULTIPROCESSING_POOL_SIZE,
        initializer=pool_initializer,
        maxtasksperchild=1
    )
    shard_pool.map(extract_page_documents, paginator.page_range)
    shard_pool.close()  # There will be no more tasks added
    shard_pool.join()  # Wait for the results before moving on

    # Refresh the index after bulk load ( at the end )
    es.indices.refresh(INDEX_NAME)



# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process; be sure to start Celery too
