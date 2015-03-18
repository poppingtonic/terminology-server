# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import

import uuid
import os
import logging
import contextlib
import wrapt
import psycopg2

from collections import Iterable
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.conf import settings

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def time_execution(fn, args, kwargs):
    """Measure the execution time fn ( a supplied function )"""
    LOGGER.debug('Called {} with {} and {}'.format(fn.func_name, args, kwargs))
    try:
        start_time = datetime.now()
        yield fn
    finally:
        secs = (datetime.now() - start_time).total_seconds()
    LOGGER.debug('Executed {}, took {}s'.format(fn.func_name, secs))


@wrapt.decorator
def instrument(wrapped, instance, args, kwargs):
    """Central place to do instrumentation e.g log calls, profile runtime"""
    with time_execution(wrapped, args, kwargs):
        return wrapped(*args, **kwargs)


@instrument
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
        raise ValidationError("Unable to connect to db with default params: %s"
                              % params)


@instrument
def _strip_first_line(source_file_path):
    """Discard the header row before loading the data"""
    temp_file_name = "/tmp/" + uuid.uuid4().get_hex() + ".tmp"
    with open(source_file_path, mode='r') as source:
        with open(temp_file_name, 'w') as dest:
            lines = [
                force_str(source_line)
                for source_line in source.readlines()[1:]
            ]
            dest.writelines(lines)

            LOGGER.debug('Written out %s' % temp_file_name)
            return temp_file_name  # Should exist from here

    # Exiting from here is a bug
    raise ValidationError('Unable to rewrite %s' % source_file_path)


@instrument
def _confirm_param_is_an_iterable(param):
    """Used below to enforce the invariant that the param should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


@instrument
def _load(table_name, file_path_list, cols):
    """The actual worker method that reads the data into the database"""
    _confirm_param_is_an_iterable(file_path_list)
    with _acquire_psycopg2_connection() as conn:
        LOGGER.debug('Acquired a psycopg2 connection')
        with conn.cursor() as cur:
            LOGGER.debug('Created a cursor')
            for file_path in file_path_list:
                rewritten_file = _strip_first_line(file_path)
                LOGGER.debug('Loading %s ( rewritten at %s )' %
                             (file_path, rewritten_file))
                with open(rewritten_file) as rewrite:
                    LOGGER.debug('Opened %s' % rewritten_file)
                    cur.copy_from(
                        rewrite, table_name, size=32768, columns=cols)
                    cur.execute('ANALYZE {};'.format(table_name))

                # Now remove the temp file ( CircleCI disk quota!! )
                os.remove(rewritten_file)

    conn.commit()


@instrument
def _execute_and_commit(statement):
    """Execute an SQL statement; used to parallelize view refereshes"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
    conn.commit()


@instrument
def load_concepts(file_path_list):
    """Load concepts from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_concept_full', file_path_list,
          ['component_id', 'effective_time', 'active',
           'module_id', 'definition_status_id'])


@instrument
def load_descriptions(file_path_list):
    """Load descriptions from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_description_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'concept_id', 'language_code', 'type_id', 'term',
           'case_significance_id'])


@instrument
def load_relationships(file_path_list):
    """Load relationships from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_relationship_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'source_id', 'destination_id', 'relationship_group', 'type_id',
           'characteristic_type_id', 'modifier_id'])


@instrument
def load_text_definitions(file_path_list):
    """Delegate to the description loading logic
    :param file_path_list:
    """
    load_descriptions(file_path_list)


@instrument
def load_simple_reference_sets(file_path_list):
    """Load simple reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_simple_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id'])


@instrument
def load_ordered_reference_sets(file_path_list):
    """Load ordered reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_ordered_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', '"order"', 'linked_to_id'])


@instrument
def load_attribute_value_reference_sets(file_path_list):
    """Load attribute value reference set from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_attribute_value_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'value_id'])


@instrument
def load_simple_map_reference_sets(file_path_list):
    """Load simple map reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_simple_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_target'])


@instrument
def load_complex_map_int_reference_sets(file_path_list):
    """Load complex map reference sets from RF2 distribution files

    :param file_path_list:
    """
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id'])


@instrument
def load_complex_map_gb_reference_sets(file_path_list):
    """Like for INTernational above, but with an extra map_block column

    For United Kingdom SNOMED->OPCS and SNOMED->ICD 10 maps
    """
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_block'])


@instrument
def load_extended_map_reference_sets(file_path_list):
    """Load extended map reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_extended_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_category_id'])


@instrument
def load_language_reference_sets(file_path_list):
    """Load language reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_language_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'acceptability_id'])


@instrument
def load_query_specification_reference_sets(file_path_list):
    """
    Load query specification reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_query_specification_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'query'])


@instrument
def load_annotation_reference_sets(file_path_list):
    """Load annotation reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_annotation_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'annotation'])


@instrument
def load_association_reference_sets(file_path_list):
    """Load association reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_association_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'target_component_id'])


@instrument
def load_module_dependency_reference_sets(file_path_list):
    """Load module dependency reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_module_dependency_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'source_effective_time',
           'target_effective_time'])


@instrument
def load_description_format_reference_sets(file_path_list):
    """Load description format reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_description_format_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'description_format_id',
           'description_length'])


@instrument
def load_refset_descriptor_reference_sets(file_path_list):
    """Load refset descriptor refsets from the RF2 distribution file

    :param file_path_list:
    """
    _load('snomed_reference_set_descriptor_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'attribute_description_id',
           'attribute_type_id', 'attribute_order'])


@instrument
def load_description_type_reference_sets(file_path_list):
    """Delegate to the description format reference set loader
    :param file_path_list:
    """
    load_description_format_reference_sets(file_path_list)


@instrument
def refresh_materialized_views():
    """This is also used by external code; e.g after authoring"""
    _execute_and_commit("SELECT RefreshAllMaterializedViews();")


@instrument
def load_release_files(path_dict):
    """Take a dict from discover.py->enumerate_release_files & trigger db load

    Because we do not have foreign keys ( intentional ), we can parallelize ops

    :param path_dict:
    """
    load_concepts(path_dict["CONCEPTS"])
    load_descriptions(path_dict["DESCRIPTIONS"])
    load_relationships(path_dict["RELATIONSHIPS"])
    load_text_definitions(path_dict["TEXT_DEFINITIONS"])
    load_language_reference_sets(path_dict["LANGUAGE_REFERENCE_SET"])
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
