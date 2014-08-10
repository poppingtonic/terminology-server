# coding=utf-8
"""Helper functions for search"""
from .search_shared import ConceptMapping


def search():
    """Wrap the raw Elasticsearch operations"""
    searcher = ConceptMapping.search()
    # TODO Ensure that all queries have 25 items as default item number
