# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import

import uuid
import multiprocessing
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
MULTIPROCESSING_POOL_SIZE = multiprocessing.cpu_count()


@contextlib.contextmanager
def time_execution(fn):
    """Measure the execution time fn ( a supplied function )"""
    try:
        start_time = datetime.now()
        yield
    finally:
        secs = (datetime.now() - start_time).total_seconds()
    LOGGER.debug('EXECUTED {}, took {}s'.format(fn.func_name, secs))


@wrapt.decorator
def instrument(wrapped, instance, args, kwargs):
    """Central place to do instrumentation e.g log calls, profile runtime"""
    with time_execution(wrapped):
        return wrapped(*args, **kwargs)


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
            return temp_file_name  # Should exist from here

    # Exiting from here is a bug
    raise ValidationError('Unable to rewrite %s' % source_file_path)


def _confirm_param_is_an_iterable(param):
    """Used below to enforce the invariant that the param should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


def _load(table_name, file_path_list, cols):
    """The actual worker method that reads the data into the database"""
    _confirm_param_is_an_iterable(file_path_list)
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            for file_path in file_path_list:
                rewritten_file = _strip_first_line(file_path)
                with open(rewritten_file) as rewrite:
                    cur.copy_from(
                        rewrite, table_name, size=32768, columns=cols)
                    cur.execute('ANALYZE {};'.format(table_name))

                # Now remove the temp file ( CircleCI disk quota!! )
                os.remove(rewritten_file)

    conn.commit()


def _execute_and_commit(statement, view_name=None):
    """Execute an SQL statement; used to parallelize view refereshes"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
            if view_name:
              cur.execute('ANALYZE {};'.format(view_name))
    conn.commit()


def execute_map_on_pool(callable_input_map,
                        process_count=MULTIPROCESSING_POOL_SIZE):
    """The obvious choice ( Pool ) has not been used because it does not play
    well with our performance measuring decorator

    :param: callable_input_map
    """
    processes = [
        multiprocessing.Process(target=fn, args=(inp,) if inp is not None else ())
        for fn, inp in callable_input_map.iteritems()
    ]
    for p in processes:
      p.start()
    for p in processes:
      p.join()


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
def refresh_snomed_concept_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_concept;",
      view_name='snomed_concept'
    )


@instrument
def refresh_snomed_description_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_description;",
      view_name='snomed_description'
    )


@instrument
def refresh_snomed_relationship_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_relationship;",
      view_name='snomed_relationship'
    )


@instrument
def refresh_snomed_annotation_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_annotation_reference_set;",
      view_name='snomed_annotation_reference_set'
    )


@instrument
def refresh_snomed_association_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_association_reference_set;",
      view_name='snomed_association_reference_set'
    )


@instrument
def refresh_snomed_attribute_value_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_attribute_value_reference_set;",
      view_name='snomed_attribute_value_reference_set'
    )


@instrument
def refresh_snomed_complex_map_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_complex_map_reference_set;",
      view_name='snomed_complex_map_reference_set'
    )


@instrument
def refresh_snomed_description_format_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_description_format_reference_set;",
      view_name='snomed_description_format_reference_set'
    )


@instrument
def refresh_snomed_extended_map_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_extended_map_reference_set;",
      view_name='snomed_extended_map_reference_set'
    )


@instrument
def refresh_snomed_language_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_language_reference_set;",
      view_name='snomed_language_reference_set'
    )


@instrument
def refresh_snomed_module_dependency_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_module_dependency_reference_set;",
      view_name='snomed_module_dependency_reference_set'
    )


@instrument
def refresh_snomed_ordered_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_ordered_reference_set;",
      view_name='snomed_ordered_reference_set'
    )


@instrument
def refresh_snomed_query_specification_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_query_specification_reference_set;",
      view_name='snomed_query_specification_reference_set'
    )


@instrument
def refresh_snomed_refset_descriptor_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW "
      "snomed_reference_set_descriptor_reference_set;",
      view_name='snomed_reference_set_descriptor_reference_set'
    )


@instrument
def refresh_snomed_simple_map_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_simple_map_reference_set;",
      view_name='snomed_simple_map_reference_set'
    )


@instrument
def refresh_snomed_simple_reference_set_materialized_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW snomed_simple_reference_set;",
      view_name='snomed_simple_reference_set'
    )


@instrument
def refresh_snomed_subsumption_materialized_view():
    _execute_and_commit("REFRESH MATERIALIZED VIEW snomed_subsumption;",
      view_name='snomed_subsumption'
    )


@instrument
def refresh_concept_preferred_terms_materialized_view():
    _execute_and_commit("REFRESH MATERIALIZED VIEW concept_preferred_terms;",
      view_name='concept_preferred_terms'
    )


@instrument
def refresh_concept_expanded_view():
    _execute_and_commit("REFRESH MATERIALIZED VIEW concept_expanded_view;",
      view_name='concept_expanded_view'
    )


@instrument
def refresh_relationship_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW relationship_expanded_view;",
      view_name='relationship_expanded_view'
    )


@instrument
def refresh_description_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW description_expanded_view;",
      view_name='description_expanded_view'
    )


@instrument
def refresh_reference_set_descriptor_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW "
      "reference_set_descriptor_reference_set_expanded_view;",
      view_name='reference_set_descriptor_reference_set_expanded_view'
    )


@instrument
def refresh_simple_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW simple_reference_set_expanded_view;",
      view_name='simple_reference_set_expanded_view'
    )


@instrument
def refresh_ordered_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW ordered_reference_set_expanded_view;",
      view_name='ordered_reference_set_expanded_view'
    )


@instrument
def refresh_attribute_value_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW attribute_value_reference_set_expanded_view;",
      view_name='attribute_value_reference_set_expanded_view'
    )


@instrument
def refresh_simple_map_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW simple_map_reference_set_expanded_view;",
      view_name='simple_map_reference_set_expanded_view'
    )


@instrument
def refresh_complex_map_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW complex_map_reference_set_expanded_view;",
      view_name='complex_map_reference_set_expanded_view'
    )


@instrument
def refresh_extended_map_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW extended_map_reference_set_expanded_view;",
      view_name='extended_map_reference_set_expanded_view'
    )


@instrument
def refresh_language_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW language_reference_set_expanded_view;",
      view_name='language_reference_set_expanded_view'
    )


@instrument
def refresh_query_specification_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW "
      "query_specification_reference_set_expanded_view;",
      view_name='query_specification_reference_set_expanded_view'
    )


@instrument
def refresh_annotation_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW annotation_reference_set_expanded_view;",
      view_name='annotation_reference_set_expanded_view'
    )


@instrument
def refresh_association_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW association_reference_set_expanded_view;",
      view_name='association_reference_set_expanded_view'
    )


@instrument
def refresh_module_dependency_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW "
      "module_dependency_reference_set_expanded_view;",
      view_name='module_dependency_reference_set_expanded_view'
    )


@instrument
def refresh_description_format_reference_set_expanded_view():
    _execute_and_commit(
      "REFRESH MATERIALIZED VIEW "
      "description_format_reference_set_expanded_view;",
      view_name='description_format_reference_set_expanded_view'
    )


def refresh_materialized_views():
    """This is also used by external code; e.g after authoring

    As an entry point method, it is not "intrumented" for performance
    measurement; that would simply make the console output less readable
    """
    execute_map_on_pool({
        refresh_snomed_concept_materialized_view: None,
        refresh_snomed_description_materialized_view: None,
        refresh_snomed_relationship_materialized_view: None,
        refresh_snomed_annotation_reference_set_materialized_view: None,
        refresh_snomed_association_reference_set_materialized_view: None,
        refresh_snomed_attribute_value_reference_set_materialized_view: None,
        refresh_snomed_complex_map_reference_set_materialized_view: None,
        refresh_snomed_description_format_reference_set_materialized_view: None,
        refresh_snomed_extended_map_reference_set_materialized_view: None,
        refresh_snomed_language_reference_set_materialized_view: None,
        refresh_snomed_module_dependency_reference_set_materialized_view: None,
        refresh_snomed_ordered_reference_set_materialized_view: None,
        refresh_snomed_query_specification_reference_set_materialized_view: None,
        refresh_snomed_refset_descriptor_reference_set_materialized_view: None,
        refresh_snomed_simple_map_reference_set_materialized_view: None,
        refresh_snomed_simple_reference_set_materialized_view: None,
        refresh_snomed_subsumption_materialized_view: None,
        refresh_concept_preferred_terms_materialized_view: None
    })
    
    # Expensive and has dependencies / is depended on, ao it runs alone
    refresh_concept_expanded_view() 

    execute_map_on_pool({
        refresh_relationship_expanded_view: None,
        refresh_description_expanded_view: None,
        refresh_reference_set_descriptor_reference_set_expanded_view: None,
        refresh_simple_reference_set_expanded_view: None,
        refresh_ordered_reference_set_expanded_view: None,
        refresh_attribute_value_reference_set_expanded_view: None,
        refresh_simple_map_reference_set_expanded_view: None,
        refresh_complex_map_reference_set_expanded_view: None,
        refresh_extended_map_reference_set_expanded_view: None,
        refresh_language_reference_set_expanded_view: None,
        refresh_query_specification_reference_set_expanded_view: None,
        refresh_annotation_reference_set_expanded_view: None,
        refresh_association_reference_set_expanded_view: None,
        refresh_module_dependency_reference_set_expanded_view: None,
        refresh_description_format_reference_set_expanded_view: None
    })


def load_release_files(path_dict):
    """Take a dict from discover.py->enumerate_release_files & trigger db load

    As an entry point method, it is not "intrumented" for performance
    measurement; that would simply make the console output less readable

    :param path_dict:
    """
    execute_map_on_pool({
      load_concepts: path_dict["CONCEPTS"],
      load_descriptions: path_dict["DESCRIPTIONS"],
      load_relationships: path_dict["RELATIONSHIPS"],
      load_text_definitions: path_dict["TEXT_DEFINITIONS"],
      load_language_reference_sets: path_dict["LANGUAGE_REFERENCE_SET"],
      load_simple_reference_sets: path_dict["SIMPLE_REFERENCE_SET"],
      load_ordered_reference_sets: path_dict["ORDERED_REFERENCE_SET"],
      load_attribute_value_reference_sets: 
        path_dict["ATTRIBUTE_VALUE_REFERENCE_SET"],
      load_simple_map_reference_sets: path_dict["SIMPLE_MAP_REFERENCE_SET"],
      load_complex_map_int_reference_sets: 
        path_dict["COMPLEX_MAP_INT_REFERENCE_SET"],
      load_complex_map_gb_reference_sets: 
        path_dict["COMPLEX_MAP_GB_REFERENCE_SET"],
      load_extended_map_reference_sets: 
        path_dict["EXTENDED_MAP_REFERENCE_SET"],
      load_query_specification_reference_sets: 
        path_dict["QUERY_SPECIFICATION_REFERENCE_SET"],
      load_annotation_reference_sets: path_dict["ANNOTATION_REFERENCE_SET"],
      load_association_reference_sets: path_dict["ASSOCIATION_REFERENCE_SET"],
      load_module_dependency_reference_sets: 
        path_dict["MODULE_DEPENDENCY_REFERENCE_SET"],
      load_description_format_reference_sets: 
        path_dict["DESCRIPTION_FORMAT_REFERENCE_SET"],
      load_refset_descriptor_reference_sets: path_dict["REFSET_DESCRIPTOR"],
      load_description_type_reference_sets: path_dict["DESCRIPTION_TYPE"]
    })
