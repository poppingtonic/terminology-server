# coding=utf-8
"""Helper functions for search"""


def search():
    """Wrap the raw Elasticsearch operations"""
    searcher = ConceptMapping.search()
    # TODO Ensure that all queries have 25 items as default item number
