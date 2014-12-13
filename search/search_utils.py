# coding=utf-8
"""Helpers and assorted utilities"""
from collections import defaultdict
from .search_shared import WORD_EQUIVALENTS_PATH, SYNONYMS_FILE_NAME

import csv


def generate_synonyms_file():
    """Process SNOMED word equivalents and generate Solr format synonyms"""
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
