# coding=utf-8
"""Helper functions for search"""

def search():
    """Wrap the raw Elasticsearch operations"""
    # TODO Ensure that all queries have 25 items as default item number
    # TODO Highlight


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

// attempt 2 - quarter way decent results
{
  "query" : {
    "match": {
       "descriptions_autocomplete": {
            "query": "myocardial infarc",
           "type": "phrase_prefix",
           "cutoff_frequency": 0.01,
           "fuzziness": "AUTO"
       }
    }
  }
}

// attempt 3 - seems to work even better, esp. after fixing indexing
{
  "query" : {
    "match": {
       "descriptions": {
            "query": "myocardial infarction",
           "type": "phrase",
           "cutoff_frequency": 0.01,
           "fuzziness": "AUTO"
       }
    }
  }
}

// attempt 4 - with stopwords analyzer
{
  "query" : {
    "match": {
       "descriptions": {
            "query": "a myocardial infarcti",
           "operator": "or",
            "analyzer": "stop",
           "type": "phrase_prefix",
           "cutoff_frequency": 0.01,
           "fuzziness": "AUTO"
       }
    }
  }
}

// attempt 5 - a "regular" match works ( no need for stop removal )
{
  "query" : {
    "match": {
       "descriptions": {
            "query": "a myocardial infarcti",
           "operator": "or",
           "cutoff_frequency": 0.01,
           "fuzziness": "AUTO"
       }
    }
  }
}

// attempt 6 - good 'ol match also handles spelling issues with minimal fuss
{
  "query" : {
    "match": {
       "descriptions": {
            "query": "a myocardial infrction",
            "cutoff_frequency": 0.01,
            "fuzziness": "AUTO"
       }
    }
  }
}

// attempt 7 - some filtering in the mix
{
"query": {
  "filtered": {
    "query": {
      "match": {
        "descriptions": {
          "query": "a myocardial infrcton",
          "cutoff_frequency": 0.01,
          "fuzziness": "AUTO"
        }
      }
    },
    "filter": {
      "bool": {
        "must": [
            {"terms": {"active": [false]}}
        ]
      }
    }
  }
}
}
"""
