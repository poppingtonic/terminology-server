# coding=utf-8
"""Helpers and assorted utilities"""
from django.utils import timezone
from collections import defaultdict
from .search_shared import WORD_EQUIVALENTS_PATH, SYNONYMS_FILE_NAME

import csv


class Timer(object):
    """Context manager to time potentially slow code blocks ( development aid )"""

    def __enter__(self):
        self.start = timezone.now()
        return self

    def __exit__(self, *args):
        self.end = timezone.now()
        self.delta = self.end - self.start
        self.interval = self.delta.total_seconds()


def generate_synonyms_file():
    """Process the SNOMED word equivalents file and generate a Solr format synonyms file for ElasticSearch"""
    reordered_dict = defaultdict(list)
    with open(WORD_EQUIVALENTS_PATH) as f:
        contents = csv.DictReader(f, delimiter='\t')
        for entry in contents:
            reordered_dict[entry['WORDBLOCKNUMBER']].append(entry['WORDTEXT'])

    final_list = []
    for v in reordered_dict.itervalues():
        final_list.append(", ".join(item for item in v))

    with open(SYNONYMS_FILE_NAME, 'w') as output_file:
        output_file.writelines("\n".join(final_list))


# Re-generate the synonyms file with each import
generate_synonyms_file()
