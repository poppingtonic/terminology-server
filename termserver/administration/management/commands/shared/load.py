# coding=utf-8
"""The actual loading of SNOMED data into the database"""
__author__ = 'ngurenyaga'

from django.core.exceptions import ValidationError
from collections import Iterable


def _confirm_param_is_an_iterable(param):
    """A helper, used by the methods below to enforce the invariant that their sole parameter should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


def _load_concepts(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_descriptions(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_relationships(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_text_definitions(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_identifiers(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_stated_relationships(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_simple_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_ordered_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_attribute_value_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_simple_map_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_complex_map_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_extended_map_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_language_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_query_specification_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_annotation_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_association_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_module_dependency_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_description_format_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_refset_descriptor_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def _load_description_type_reference_sets(file_path_list):
    _confirm_param_is_an_iterable(file_path_list)
    pass


def load_release_files(path_dict):
    """Accept a dict output by discover.py->enumerate_release_files and trigger database loading"""
    _load_concepts(["CONCEPTS"])
    _load_descriptions(path_dict["DESCRIPTIONS"])
    _load_relationships(path_dict["RELATIONSHIPS"])
    _load_text_definitions(path_dict["TEXT_DEFINITIONS"])
    _load_stated_relationships(["STATED_RELATIONSHIPS"])
    _load_simple_reference_sets(path_dict["SIMPLE_REFERENCE_SET"])
    _load_ordered_reference_sets(path_dict["ORDERED_REFERENCE_SET"])
    _load_attribute_value_reference_sets(path_dict["ATTRIBUTE_VALUE_REFERENCE_SET"])
    _load_simple_map_reference_sets(path_dict["SIMPLE_MAP_REFERENCE_SET"])
    _load_complex_map_reference_sets(path_dict["COMPLEX_MAP_REFERENCE_SET"])
    _load_extended_map_reference_sets(path_dict["EXTENDED_MAP_REFERENCE_SET"])
    _load_language_reference_sets(["LANGUAGE_REFERENCE_SET"])
    _load_query_specification_reference_sets(["QUERY_SPECIFICATION_REFERENCE_SET"])
    _load_annotation_reference_sets(path_dict["ANNOTATION_REFERENCE_SET"])
    _load_association_reference_sets(path_dict["ASSOCIATION_REFERENCE_SET"])
    _load_module_dependency_reference_sets(path_dict["MODULE_DEPENDENCY_REFERENCE_SET"])
    _load_description_format_reference_sets(path_dict["DESCRIPTION_FORMAT_REFERENCE_SET"])
    _load_refset_descriptor_reference_sets(["REFSET_DESCRIPTOR"])
    _load_description_type_reference_sets(path_dict["DESCRIPTION_TYPE"])
    _load_identifiers(path_dict["IDENTIFIER"])
