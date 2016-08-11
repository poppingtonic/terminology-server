# coding=utf-8
"""Enumerate the SNOMED files that are in the designated directory"""
import os

from collections import defaultdict
from sil_snomed_server.config import config

def _join(base, path):
    """A helper - for readability / brevity"""
    return os.path.join(base, path)

CONTENT_FOLDER = os.path.join(
    config.basedir, 'data/extracted_terminology_data')
SUBFOLDERS = {
    'CONCEPTS':
    _join(CONTENT_FOLDER, 'concepts'),
    'DESCRIPTIONS':
    _join(CONTENT_FOLDER, 'descriptions'),
    'RELATIONSHIPS':
    _join(CONTENT_FOLDER, 'relationships'),
    'TEXT_DEFINITIONS':
    _join(CONTENT_FOLDER, 'text_definitions'),
    'IDENTIFIER':
    _join(CONTENT_FOLDER, 'identifiers'),
    'STATED_RELATIONSHIPS':
    _join(CONTENT_FOLDER, 'stated_relationships'),
    'SIMPLE_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'simple_reference_sets'),
    'ORDERED_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'ordered_reference_sets'),
    'ATTRIBUTE_VALUE_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'attribute_value_reference_sets'),
    'SIMPLE_MAP_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'simple_map_reference_sets'),
    'COMPLEX_MAP_INT_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'complex_map_int_reference_sets'),
    'COMPLEX_MAP_GB_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'complex_map_gb_reference_sets'),
    'EXTENDED_MAP_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'extended_map_reference_sets'),
    'LANGUAGE_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'language_reference_sets'),
    'QUERY_SPECIFICATION_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'query_specification_reference_sets'),
    'ANNOTATION_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'annotation_reference_sets'),
    'ASSOCIATION_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'association_reference_sets'),
    'MODULE_DEPENDENCY_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'module_dependency_reference_sets'),
    'DESCRIPTION_FORMAT_REFERENCE_SET':
    _join(CONTENT_FOLDER, 'description_format_reference_sets'),
    'REFSET_DESCRIPTOR':
    _join(CONTENT_FOLDER, 'refset_descriptor_reference_sets'),
    'DESCRIPTION_TYPE':
    _join(CONTENT_FOLDER, 'description_type_reference_sets')
}
SOURCE_FILES = defaultdict(list, {
    key: [os.path.join(subfolder, fname) for fname in os.listdir(subfolder)]
    for key, subfolder in iter(SUBFOLDERS.items())
})


def enumerate_release_files():
    """List and categorize the files that are part of a full clinical release

    :param release_type:
    """
    return SOURCE_FILES
