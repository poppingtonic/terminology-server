# coding=utf-8
"""Classes and modules that are shared between indexing and searching"""
from elasticutils.contrib.django import MappingType, Indexable

# We only plan to have one index, one type; so these can be constants
INDEX_NAME = 'concept-index'
INDEX_BATCH_SIZE = 1000
MAPPING_TYPE_NAME = 'concept'


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
