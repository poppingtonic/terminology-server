# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import

from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.conf import settings
from django.db import transaction
from collections import Iterable
from celery import shared_task


import psycopg2
import uuid
import traceback


def _acquire_psycopg2_connection():
    """Relies on default Django settings for database connection parameters"""
    try:
        params = (
            "dbname='%(NAME)s' user='%(USER)s' host='%(HOST)s' "
            "password='%(PASSWORD)s' port='%(PORT)s'" %
            settings.DATABASES["default"]
        )
        return psycopg2.connect(params)
    except:
        raise ValidationError(
            "Unable to connect to db with default parameters")


def _strip_first_line(source_file_path):
    """Discard the header row before loading the data"""
    temp_file_name = "/tmp/" + uuid.uuid4().get_hex() + ".tmp"
    with source_file_path.open(mode='rU', encoding='UTF-8') as source:
        with open(temp_file_name, 'w') as dest:
            lines = [
                force_str(source_line)
                for source_line in source.readlines()[1:]
            ]
            try:
                dest.writelines(lines)
            except TypeError as ex:
                print('Error: %s' % ex)
                traceback.print_exc()
    return temp_file_name


def _load(table_name, file_path_list, cols):
    """The actual worker method that reads the data into the database"""
    _confirm_param_is_an_iterable(file_path_list)
    with _acquire_psycopg2_connection() as conn:
        for file_path in file_path_list:
            with open(_strip_first_line(file_path)) as f:
                with conn.cursor() as cur:
                    cur.copy_from(f, table_name, columns=cols)
        conn.commit()


def _confirm_param_is_an_iterable(param):
    """Used below to enforce the invariant that the param should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


@shared_task
def load_concepts(file_path_list):
    """Load concepts from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_concept_full', file_path_list,
          ['component_id', 'effective_time', 'active',
           'module_id', 'definition_status_id'])


@shared_task
def load_descriptions(file_path_list):
    """Load descriptions from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_description_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'concept_id', 'language_code', 'type_id', 'term',
           'case_significance_id'])


@shared_task
def load_relationships(file_path_list):
    """Load relationships from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_relationship_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'source_id', 'destination_id', 'relationship_group', 'type_id',
           'characteristic_type_id', 'modifier_id'])


@shared_task
def load_text_definitions(file_path_list):
    """Delegate to the description loading logic
    :param file_path_list:
    """
    load_descriptions(file_path_list)


@shared_task
def load_simple_reference_sets(file_path_list):
    """Load simple reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_simple_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id'])


@shared_task
def load_ordered_reference_sets(file_path_list):
    """Load ordered reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_ordered_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', '"order"', 'linked_to_id'])


@shared_task
def load_attribute_value_reference_sets(file_path_list):
    """Load attribute value reference set from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_attribute_value_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'value_id'])


@shared_task
def load_simple_map_reference_sets(file_path_list):
    """Load simple map reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_simple_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_target'])


@shared_task
def load_complex_map_int_reference_sets(file_path_list):
    """Load complex map reference sets from RF2 distribution files

    :param file_path_list:
    """
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id'])


@shared_task
def load_complex_map_gb_reference_sets(file_path_list):
    """Like for INTernational above, but with an extra map_block column

    For United Kingdom SNOMED->OPCS and SNOMED->ICD 10 maps
    """
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_block'])


@shared_task
def load_extended_map_reference_sets(file_path_list):
    """Load extended map reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_extended_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_category_id'])


@shared_task
def load_language_reference_sets(file_path_list):
    """Load language reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_language_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'acceptability_id'])


@shared_task
def load_query_specification_reference_sets(file_path_list):
    """
    Load query specification reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_query_specification_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'query'])


@shared_task
def load_annotation_reference_sets(file_path_list):
    """Load annotation reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_annotation_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'annotation'])


@shared_task
def load_association_reference_sets(file_path_list):
    """Load association reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_association_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'target_component_id'])


@shared_task
def load_module_dependency_reference_sets(file_path_list):
    """Load module dependency reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_module_dependency_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'source_effective_time',
           'target_effective_time'])


@shared_task
def load_description_format_reference_sets(file_path_list):
    """Load description format reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_description_format_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'description_format_id',
           'description_length'])


@shared_task
def load_refset_descriptor_reference_sets(file_path_list):
    """Load refset descriptor refsets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_reference_set_descriptor_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'attribute_description_id',
           'attribute_type_id', 'attribute_order'])


@shared_task
def load_description_type_reference_sets(file_path_list):
    """Delegate to the description format reference set loader
    :param file_path_list:
    """
    load_description_format_reference_sets(file_path_list)


@shared_task
def refresh_materialized_views():
    """Pre-compute the views that will power production queries"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            # Core component views
            cur.execute("REFRESH MATERIALIZED VIEW snomed_subsumption;")
            cur.execute("REFRESH MATERIALIZED VIEW concept_preferred_terms;")
            cur.execute("REFRESH MATERIALIZED VIEW con_desc_cte;")
            cur.execute("REFRESH MATERIALIZED VIEW concept_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW relationship_expanded_view;")
            cur.execute("REFRESH MATERIALIZED VIEW description_expanded_view;")

            # Refset views
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "reference_set_descriptor_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "simple_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "ordered_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "attribute_value_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "simple_map_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "complex_map_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "extended_map_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "language_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "query_specification_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "annotation_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "association_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "module_dependency_reference_set_expanded_view;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "description_format_reference_set_expanded_view;")

        # Commit after refreshing all views
        conn.commit()


@shared_task
def refresh_dynamic_snapshot():
    """Dynamically create a 'most recent snapshot' view"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            # Core component views
            cur.execute("REFRESH MATERIALIZED VIEW snomed_concept;")
            cur.execute("REFRESH MATERIALIZED VIEW snomed_description;")
            cur.execute("REFRESH MATERIALIZED VIEW snomed_relationship;")

            # Refset views
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "snomed_reference_set_descriptor_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_simple_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_ordered_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "snomed_attribute_value_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_simple_map_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_complex_map_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_extended_map_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_language_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "snomed_query_specification_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_annotation_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW snomed_association_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "snomed_module_dependency_reference_set;")
            cur.execute(
                "REFRESH MATERIALIZED VIEW "
                "snomed_description_format_reference_set;")

        # Commit after refreshing all views
        conn.commit()


def load_release_files(path_dict):
    """Take a dict from discover.py->enumerate_release_files & trigger db load

    :param path_dict:
    """
    with transaction.atomic():
        load_concepts(path_dict["CONCEPTS"])
        load_descriptions(path_dict["DESCRIPTIONS"])
        load_relationships(path_dict["RELATIONSHIPS"])
        load_text_definitions(path_dict["TEXT_DEFINITIONS"])
        load_simple_reference_sets(path_dict["SIMPLE_REFERENCE_SET"])
        load_ordered_reference_sets(path_dict["ORDERED_REFERENCE_SET"])
        load_attribute_value_reference_sets(
            path_dict["ATTRIBUTE_VALUE_REFERENCE_SET"])
        load_simple_map_reference_sets(path_dict["SIMPLE_MAP_REFERENCE_SET"])
        load_complex_map_int_reference_sets(
            path_dict["COMPLEX_MAP_INT_REFERENCE_SET"])
        load_complex_map_gb_reference_sets(
            path_dict["COMPLEX_MAP_GB_REFERENCE_SET"])
        load_extended_map_reference_sets(
            path_dict["EXTENDED_MAP_REFERENCE_SET"])
        load_language_reference_sets(path_dict["LANGUAGE_REFERENCE_SET"])
        load_query_specification_reference_sets(
            path_dict["QUERY_SPECIFICATION_REFERENCE_SET"])
        load_annotation_reference_sets(path_dict["ANNOTATION_REFERENCE_SET"])
        load_association_reference_sets(path_dict["ASSOCIATION_REFERENCE_SET"])
        load_module_dependency_reference_sets(
            path_dict["MODULE_DEPENDENCY_REFERENCE_SET"])
        load_description_format_reference_sets(
            path_dict["DESCRIPTION_FORMAT_REFERENCE_SET"])
        load_refset_descriptor_reference_sets(path_dict["REFSET_DESCRIPTOR"])
        load_description_type_reference_sets(path_dict["DESCRIPTION_TYPE"])
