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
import multiprocessing
import logging

LOGGER = logging.getLogger(__name__)
MULTIPROCESSING_POOL_SIZE = multiprocessing.cpu_count()


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


def _process_initializer():
    """Called upon the start of each process in the multiprocessing pool"""
    LOGGER.debug('Starting %s' % multiprocessing.current_process().name)


def _execute_and_commit(statement):
    """Execute an SQL statement; used to parallelize view refereshes"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
    conn.commit()


def _create_multiprocessing_pool():
    """A helper"""
    return multiprocessing.Pool(
        processes=MULTIPROCESSING_POOL_SIZE,
        initializer=_process_initializer,
        maxtasksperchild=10
    )


def _execute_on_pool(statements):
    """Execute a list / iterable of statements on a multiprocessing pool"""
    pool = _create_multiprocessing_pool()
    pool.map(_execute_and_commit, statements)
    pool.close()  # There will be no more tasks added
    pool.join()  # Wait for the results before moving on


def _execute_map_on_pool(callable_input_map):
    """Multiprocessing pool that does not use the same callable for all inputs

    Differs from the function above in that this one does not apply the same
    callable to all of the inputs. It expects an input map where the keys are
    callables and the values are arguments for the corresponding callables

    :param: callable_input_map
    """
    pool = _create_multiprocessing_pool()
    for fn, input_map in callable_input_map.iteritems():
        pool.apply_async(fn, args=(input_map,))
    pool.close()  # There will be no more tasks added
    pool.join()  # Wait for the results before moving on


def _create_component_source_table_indexes():
    """Create indexes for the component source tables

    Index creation is delayed so as to reduce its impact on data load times
    """
    _execute_on_pool([
        "CREATE INDEX con_effective_time ON "
        "snomed_concept_full(effective_time, component_id);",
        "CREATE INDEX desc_effective_time ON "
        "snomed_description_full(effective_time, component_id);",
        "CREATE INDEX rel_effective_time ON "
        "snomed_relationship_full(effective_time, component_id);"
    ])


def _create_component_snapshot_indexes():
    """Create indexes for the component snapshot tables

    Index creation is delayed so as to reduce its impact on data load times
    """
    _execute_on_pool([
        "CREATE INDEX concept_component_id_index ON "
        "snomed_concept(component_id);",
        "CREATE INDEX description_component_id_index ON "
        "snomed_description(component_id);",
        "CREATE INDEX description_concept_id_index ON "
        "snomed_description(concept_id);",
        "CREATE INDEX source_id_index ON "
        "snomed_relationship(source_id);",
        "CREATE INDEX destination_id_index ON "
        "snomed_relationship(destination_id);"
    ])


def _create_refset_source_table_indexes():
    """Create indexes for the refset source tables

    Index creation is delayed so as to reduce its impact on data load times
    """
    _execute_on_pool([
        "CREATE INDEX annotation_refset_effective_time ON "
        "snomed_annotation_reference_set_full(effective_time, row_id);",
        "CREATE INDEX association_refset_effective_time ON "
        "snomed_association_reference_set_full(effective_time, row_id);",
        "CREATE INDEX attribute_value_refset_effective_time ON "
        "snomed_attribute_value_reference_set_full(effective_time, row_id);",
        "CREATE INDEX complex_map_refset_effective_time ON "
        "snomed_complex_map_reference_set_full(effective_time, row_id);",
        "CREATE INDEX description_format_refset_effective_time ON "
        "snomed_description_format_reference_set_full"
        "(effective_time, row_id);",
        "CREATE INDEX extended_map_refset_effective_time ON "
        "snomed_extended_map_reference_set_full(effective_time, row_id);",
        "CREATE INDEX language_refset_effective_time ON "
        "snomed_language_reference_set_full(effective_time, row_id);",
        "CREATE INDEX module_dependency_refset_effective_time ON "
        "snomed_module_dependency_reference_set_full(effective_time, row_id);",
        "CREATE INDEX ordered_refset_effective_time ON "
        "snomed_ordered_reference_set_full(effective_time, row_id);",
        "CREATE INDEX query_specification_refset_effective_time ON "
        "snomed_query_specification_reference_set_full"
        "(effective_time, row_id);",
        "CREATE INDEX reference_set_descriptor_refset_effective_time ON "
        "snomed_reference_set_descriptor_reference_set_full"
        "(effective_time, row_id);",
        "CREATE INDEX simple_map_refset_effective_time ON "
        "snomed_simple_map_reference_set_full(effective_time, row_id);",
        "CREATE INDEX simple_refset_effective_time ON "
        "snomed_simple_reference_set_full(effective_time, row_id);"
    ])


def _create_refset_snapshot_indexes():
    """Create indexes for the refset snapshot tables

    Index creation is delayed so as to reduce its impact on data load times
    """
    _execute_on_pool([
        "CREATE INDEX annotation_refset_row ON "
        "snomed_annotation_reference_set(row_id);",
        "CREATE INDEX association_refset_row ON "
        "snomed_association_reference_set(row_id);",
        "CREATE INDEX attribute_value_refset_row ON "
        "snomed_attribute_value_reference_set(row_id);",
        "CREATE INDEX complex_map_refset_row ON "
        "snomed_complex_map_reference_set(row_id);",
        "CREATE INDEX description_format_refset_row ON "
        "snomed_description_format_reference_set"
        "(row_id);",
        "CREATE INDEX extended_map_refset_row ON "
        "snomed_extended_map_reference_set(row_id);",
        "CREATE INDEX language_refset_row ON "
        "snomed_language_reference_set(row_id);",
        "CREATE INDEX module_dependency_refset_row ON "
        "snomed_module_dependency_reference_set(row_id);",
        "CREATE INDEX ordered_refset_row ON "
        "snomed_ordered_reference_set(row_id);",
        "CREATE INDEX query_specification_refset_row ON "
        "snomed_query_specification_reference_set"
        "(row_id);",
        "CREATE INDEX reference_set_descriptor_refset_row ON "
        "snomed_reference_set_descriptor_reference_set"
        "(row_id);",
        "CREATE INDEX simple_map_refset_row ON "
        "snomed_simple_map_reference_set(row_id);",
        "CREATE INDEX simple_refset_row ON "
        "snomed_simple_reference_set(row_id);"

        "CREATE INDEX annotation_refset_component ON "
        "snomed_annotation_reference_set(referenced_component_id);",
        "CREATE INDEX association_refset_component ON "
        "snomed_association_reference_set(referenced_component_id);",
        "CREATE INDEX attribute_value_refset_component ON "
        "snomed_attribute_value_reference_set(referenced_component_id);",
        "CREATE INDEX complex_map_refset_component ON "
        "snomed_complex_map_reference_set(referenced_component_id);",
        "CREATE INDEX description_format_refset_component ON "
        "snomed_description_format_reference_set"
        "(referenced_component_id);",
        "CREATE INDEX extended_map_refset_component ON "
        "snomed_extended_map_reference_set(referenced_component_id);",
        "CREATE INDEX language_refset_component ON "
        "snomed_language_reference_set(referenced_component_id);",
        "CREATE INDEX module_dependency_refset_component ON "
        "snomed_module_dependency_reference_set(referenced_component_id);",
        "CREATE INDEX ordered_refset_component ON "
        "snomed_ordered_reference_set(referenced_component_id);",
        "CREATE INDEX query_specification_refset_component ON "
        "snomed_query_specification_reference_set"
        "(referenced_component_id);",
        "CREATE INDEX reference_set_descriptor_refset_component ON "
        "snomed_reference_set_descriptor_reference_set"
        "(referenced_component_id);",
        "CREATE INDEX simple_map_refset_component ON "
        "snomed_simple_map_reference_set(referenced_component_id);",
        "CREATE INDEX simple_refset_component ON "
        "snomed_simple_reference_set(referenced_component_id);"

        "CREATE INDEX annotationset ON "
        "snomed_annotation_reference_set(refset_id);",
        "CREATE INDEX associationset ON "
        "snomed_association_reference_set(refset_id);",
        "CREATE INDEX attribute_valueset ON "
        "snomed_attribute_value_reference_set(refset_id);",
        "CREATE INDEX complex_mapset ON "
        "snomed_complex_map_reference_set(refset_id);",
        "CREATE INDEX description_formatset ON "
        "snomed_description_format_reference_set"
        "(refset_id);",
        "CREATE INDEX extended_mapset ON "
        "snomed_extended_map_reference_set(refset_id);",
        "CREATE INDEX languageset ON "
        "snomed_language_reference_set(refset_id);",
        "CREATE INDEX module_dependencyset ON "
        "snomed_module_dependency_reference_set(refset_id);",
        "CREATE INDEX orderedset ON "
        "snomed_ordered_reference_set(refset_id);",
        "CREATE INDEX query_specificationset ON "
        "snomed_query_specification_reference_set"
        "(refset_id);",
        "CREATE INDEX reference_set_descriptorset ON "
        "snomed_reference_set_descriptor_reference_set"
        "(refset_id);",
        "CREATE INDEX simple_mapset ON "
        "snomed_simple_map_reference_set(refset_id);",
        "CREATE INDEX simpleset ON "
        "snomed_simple_reference_set(refset_id);"
    ])


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
    # These two can run in parallel, but we'll have to wait before we proceed
    _execute_on_pool([
        "REFRESH MATERIALIZED VIEW snomed_subsumption;",
        "REFRESH MATERIALIZED VIEW concept_preferred_terms;"
    ])
    _execute_on_pool([
        "CREATE INDEX snomed_subsumption_concept_id ON "
        "snomed_subsumption(concept_id);",
        "CREATE INDEX concept_preferred_terms_concept_id ON "
        "concept_preferred_terms(concept_id);"
    ])

    # This one must execute alone - hard dependency of the next view
    _execute_on_pool(["REFRESH MATERIALIZED VIEW con_desc_cte;"])
    _execute_on_pool([
        "CREATE INDEX con_desc_cte_concept_id ON con_desc_cte(concept_id);"])

    # These can execute in an embarassingly parallel manner
    _execute_on_pool([
        "REFRESH MATERIALIZED VIEW concept_expanded_view;",
        "REFRESH MATERIALIZED VIEW relationship_expanded_view;",
        "REFRESH MATERIALIZED VIEW description_expanded_view;",
        "REFRESH MATERIALIZED VIEW "
        "reference_set_descriptor_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW simple_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW ordered_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW "
        "attribute_value_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW simple_map_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW complex_map_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW extended_map_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW language_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW "
        "query_specification_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW annotation_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW association_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW "
        "module_dependency_reference_set_expanded_view;",
        "REFRESH MATERIALIZED VIEW "
        "description_format_reference_set_expanded_view;"
    ])
    _execute_on_pool([
        "CREATE INDEX concept_expanded_view_concept_id ON "
        "concept_expanded_view(concept_id);",
        "CREATE INDEX description_expanded_view_id ON "
        "description_expanded_view(id);",
        "CREATE INDEX description_expanded_view_component_id ON "
        "description_expanded_view(component_id);",
        "CREATE INDEX relationship_expanded_view_component_id ON "
        "relationship_expanded_view(component_id);",
        "CREATE INDEX relationship_expanded_view_id ON "
        "relationship_expanded_view(id);"
    ])


@shared_task
def refresh_dynamic_snapshot():
    """Dynamically create a 'most recent snapshot' view"""
    _execute_on_pool([
        "REFRESH MATERIALIZED VIEW snomed_concept;",
        "REFRESH MATERIALIZED VIEW snomed_description;",
        "REFRESH MATERIALIZED VIEW snomed_relationship;",
        "REFRESH MATERIALIZED VIEW "
        "snomed_reference_set_descriptor_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_simple_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_ordered_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_attribute_value_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_simple_map_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_complex_map_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_extended_map_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_language_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_query_specification_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_annotation_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_association_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_module_dependency_reference_set;",
        "REFRESH MATERIALIZED VIEW snomed_description_format_reference_set;"
    ])

    # Create indexes after the view creation
    _create_component_snapshot_indexes()
    _create_refset_snapshot_indexes()


def load_release_files(path_dict):
    """Take a dict from discover.py->enumerate_release_files & trigger db load

    :param path_dict:
    """
    with transaction.atomic():
        # This must run first, alone, to completion
        load_concepts(path_dict["CONCEPTS"])

        # The next three will be run together; to compl
        _execute_map_on_pool({
            load_descriptions: path_dict["DESCRIPTIONS"],
            load_relationships: path_dict["RELATIONSHIPS"],
            load_text_definitions: path_dict["TEXT_DEFINITIONS"]
        })

        # These can be parallelized willy-nilly ( no dependencies )
        _execute_map_on_pool({
            load_language_reference_sets: path_dict["LANGUAGE_REFERENCE_SET"],
            load_simple_reference_sets: path_dict["SIMPLE_REFERENCE_SET"],
            load_ordered_reference_sets: path_dict["ORDERED_REFERENCE_SET"],
            load_attribute_value_reference_sets:
            path_dict["ATTRIBUTE_VALUE_REFERENCE_SET"],
            load_simple_map_reference_sets:
            path_dict["SIMPLE_MAP_REFERENCE_SET"],
            load_complex_map_int_reference_sets:
            path_dict["COMPLEX_MAP_INT_REFERENCE_SET"],
            load_complex_map_gb_reference_sets:
            path_dict["COMPLEX_MAP_GB_REFERENCE_SET"],
            load_extended_map_reference_sets:
            path_dict["EXTENDED_MAP_REFERENCE_SET"],
            load_query_specification_reference_sets:
            path_dict["QUERY_SPECIFICATION_REFERENCE_SET"],
            load_annotation_reference_sets:
            path_dict["ANNOTATION_REFERENCE_SET"],
            load_association_reference_sets:
            path_dict["ASSOCIATION_REFERENCE_SET"],
            load_module_dependency_reference_sets:
            path_dict["MODULE_DEPENDENCY_REFERENCE_SET"],
            load_description_format_reference_sets:
            path_dict["DESCRIPTION_FORMAT_REFERENCE_SET"],
            load_refset_descriptor_reference_sets:
            path_dict["REFSET_DESCRIPTOR"],
            load_description_type_reference_sets: path_dict["DESCRIPTION_TYPE"]
        })

        # Now create the indexes
        _create_component_source_table_indexes()
        _create_refset_source_table_indexes()
