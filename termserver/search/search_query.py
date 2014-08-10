# coding=utf-8
"""Helper functions for search"""
from .search_shared import ConceptMapping


def search():
    """Wrap the raw Elasticsearch operations"""
    searcher = ConceptMapping.search()
    # TODO Ensure that all queries have 25 items as default item number


"""
// attempt 1
{
  "query" : {
    "match": {
       "descriptions": {
            "query": "myocardial infarction",
           "type": "phrase",
           "cutoff_frequency": 0.01,
           "operator": "and",
           "fuzziness": "AUTO",
           "max_expansions": 3,
          "slop": 2
       }
    }
  }
}


"""
