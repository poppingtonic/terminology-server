# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.conf import settings
from django.db import transaction
from collections import Iterable

import psycopg2
import uuid
import os
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
        raise ValidationError("Unable to connect to db with default params: %s"
                              % params)


def _strip_first_line(source_file_path):
    """Discard the header row before loading the data"""
    temp_file_name = "/tmp/" + uuid.uuid4().get_hex() + ".tmp"
    LOGGER.debug('Stripping first line of %s ( destination %s )' %
                 (source_file_path, temp_file_name))
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


def _confirm_param_is_an_iterable(param):
    """Used below to enforce the invariant that the param should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


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

                # Now remove the temp file ( CircleCI disk quota!! )
                os.remove(rewritten_file)

    conn.commit()


def _process_initializer():
    """Called upon the start of each process in the multiprocessing pool"""
    pr = multiprocessing.current_process()
    LOGGER.debug('Starting %s' % pr.name)


def _execute_and_commit(statement):
    """Execute an SQL statement; used to parallelize view refereshes"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
    conn.commit()


def _create_multiprocessing_pool(process_count):
    """A helper"""
    return multiprocessing.Pool(
        processes=process_count,
        initializer=_process_initializer,
        maxtasksperchild=100
    )


def _execute_on_pool(statements, process_count=MULTIPROCESSING_POOL_SIZE):
    """Execute a list / iterable of statements on a multiprocessing pool"""
    pool = _create_multiprocessing_pool(process_count)
    pool.map(_execute_and_commit, statements)
    pool.close()  # There will be no more tasks added
    pool.join()  # Wait for the results before moving on


def _execute_map_on_pool(callable_input_map,
                         process_count=MULTIPROCESSING_POOL_SIZE):
    """Multiprocessing pool that does not use the same callable for all inputs

    Differs from the function above in that this one does not apply the same
    callable to all of the inputs. It expects an input map where the keys are
    callables and the values are arguments for the corresponding callables

    :param: callable_input_map
    """
    pool = _create_multiprocessing_pool(process_count)
    for fn, input_map in callable_input_map.iteritems():
        pool.apply_async(fn, args=(input_map,))
    pool.close()  # There will be no more tasks added
    pool.join()  # Wait for the results before moving on


def _create_source_table_indexes():
    """Create indexes for the component source tables

    Index creation is delayed so as to reduce its impact on data load times
    """
    _execute_on_pool([
        "CREATE INDEX con_effective_time ON "
        "snomed_concept_full(effective_time, component_id);",
        "CREATE INDEX desc_effective_time ON "
        "snomed_description_full(effective_time, component_id);",
        "CREATE INDEX rel_effective_time ON "
        "snomed_relationship_full(effective_time, component_id);",
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
    ], process_count=MULTIPROCESSING_POOL_SIZE)


def load_concepts(file_path_list):
    """Load concepts from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load concepts from: %s' % file_path_list)
    _load('snomed_concept_full', file_path_list,
          ['component_id', 'effective_time', 'active',
           'module_id', 'definition_status_id'])
    LOGGER.debug('Loaded concepts from: %s' % file_path_list)


def load_descriptions(file_path_list):
    """Load descriptions from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load descriptions from: %s' % file_path_list)
    _load('snomed_description_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'concept_id', 'language_code', 'type_id', 'term',
           'case_significance_id'])
    LOGGER.debug('Loaded descriptions from: %s' % file_path_list)


def load_relationships(file_path_list):
    """Load relationships from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load relationships from: %s' % file_path_list)
    _load('snomed_relationship_full', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id',
           'source_id', 'destination_id', 'relationship_group', 'type_id',
           'characteristic_type_id', 'modifier_id'])
    LOGGER.debug('Loaded relationships from: %s' % file_path_list)


def load_text_definitions(file_path_list):
    """Delegate to the description loading logic
    :param file_path_list:
    """
    load_descriptions(file_path_list)


def load_simple_reference_sets(file_path_list):
    """Load simple reference sets from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load simple refsets from: %s' % file_path_list)
    _load('snomed_simple_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id'])
    LOGGER.debug('Loaded simple reference sets from: %s' % file_path_list)


def load_ordered_reference_sets(file_path_list):
    """Load ordered reference sets from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load ordered refsets from: %s' % file_path_list)
    _load('snomed_ordered_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', '"order"', 'linked_to_id'])
    LOGGER.debug('Loaded ordered reference sets from: %s' % file_path_list)


def load_attribute_value_reference_sets(file_path_list):
    """Load attribute value reference set from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load attr. value refsets from: %s' % file_path_list)
    _load('snomed_attribute_value_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'value_id'])
    LOGGER.debug('Loaded attribute value refsets from: %s' % file_path_list)


def load_simple_map_reference_sets(file_path_list):
    """Load simple map reference sets from RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load simple map refsets from: %s' % file_path_list)
    _load('snomed_simple_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_target'])
    LOGGER.debug('Loaded simple map refsets from: %s' % file_path_list)


def load_complex_map_int_reference_sets(file_path_list):
    """Load complex map reference sets from RF2 distribution files

    :param file_path_list:
    """
    LOGGER.debug('About to load complex maps (INT) from: %s' % file_path_list)
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id'])
    LOGGER.debug('Loaded complex map refsets (INT) from: %s' % file_path_list)


def load_complex_map_gb_reference_sets(file_path_list):
    """Like for INTernational above, but with an extra map_block column

    For United Kingdom SNOMED->OPCS and SNOMED->ICD 10 maps
    """
    LOGGER.debug('About to load complex maps (UK) from: %s' % file_path_list)
    _load('snomed_complex_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_block'])
    LOGGER.debug('Loaded complex map refsets (GB) from: %s' % file_path_list)


def load_extended_map_reference_sets(file_path_list):
    """Load extended map reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load extended maps from: %s' % file_path_list)
    _load('snomed_extended_map_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_category_id'])
    LOGGER.debug('Loaded extended map refsets from: %s' % file_path_list)


def load_language_reference_sets(file_path_list):
    """Load language reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load language refsets from: %s' % file_path_list)
    _load('snomed_language_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'acceptability_id'])
    LOGGER.debug('Loaded language reference sets from: %s' % file_path_list)


def load_query_specification_reference_sets(file_path_list):
    """
    Load query specification reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load query spec refsets from: %s' % file_path_list)
    _load('snomed_query_specification_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'query'])
    LOGGER.debug('Loaded query spec refsets from: %s' % file_path_list)


def load_annotation_reference_sets(file_path_list):
    """Load annotation reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load annotation refsets from: %s' % file_path_list)
    _load('snomed_annotation_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'annotation'])
    LOGGER.debug('Loaded annotation refsets from: %s' % file_path_list)


def load_association_reference_sets(file_path_list):
    """Load association reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load association refsets from: %s' % file_path_list)
    _load('snomed_association_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'target_component_id'])
    LOGGER.debug('Loaded association refsets from: %s' % file_path_list)


def load_module_dependency_reference_sets(file_path_list):
    """Load module dependency reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load module dep. refsets from: %s' % file_path_list)
    _load('snomed_module_dependency_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'source_effective_time',
           'target_effective_time'])
    LOGGER.debug('Loaded module dependency refsets from: %s' % file_path_list)


def load_description_format_reference_sets(file_path_list):
    """Load description format reference sets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load des. format refsets from: %s' % file_path_list)
    _load('snomed_description_format_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'description_format_id',
           'description_length'])
    LOGGER.debug('Loaded description format refsets from: %s' % file_path_list)


def load_refset_descriptor_reference_sets(file_path_list):
    """Load refset descriptor refsets from the RF2 distribution file

    :param file_path_list:
    """
    LOGGER.debug('About to load ref. descr. refsets from: %s' % file_path_list)
    _load('snomed_reference_set_descriptor_reference_set_full', file_path_list,
          ['row_id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'attribute_description_id',
           'attribute_type_id', 'attribute_order'])
    LOGGER.debug('Loaded refset descriptor refsets from: %s' % file_path_list)


def load_description_type_reference_sets(file_path_list):
    """Delegate to the description format reference set loader
    :param file_path_list:
    """
    load_description_format_reference_sets(file_path_list)


def refresh_materialized_views():
    """Pre-compute the views that will power production queries"""
    with transaction.atomic():
        # These have no dependencies but must refresh before the expanded views
        _execute_on_pool([
            "REFRESH MATERIALIZED VIEW snomed_subsumption;",
            "REFRESH MATERIALIZED VIEW concept_preferred_terms;"
        ])
        try:
            _execute_on_pool([
                "CREATE INDEX snomed_subsumption_concept_id ON "
                "snomed_subsumption(concept_id);",
                "CREATE INDEX concept_preferred_terms_concept_id ON "
                "concept_preferred_terms(concept_id);",
                "ANALYZE;"
            ])
        except psycopg2.ProgrammingError:
            LOGGER.debug('Looks like we already had indexes; '
                         'normal when refreshing on an existing database')

        _execute_on_pool([
            "REFRESH MATERIALIZED VIEW concept_expanded_view;",
            "REFRESH MATERIALIZED VIEW relationship_expanded_view;",
            "REFRESH MATERIALIZED VIEW language_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "complex_map_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW description_expanded_view;",
            "REFRESH MATERIALIZED VIEW simple_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "attribute_value_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "simple_map_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "association_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "extended_map_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW ordered_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "reference_set_descriptor_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "query_specification_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "annotation_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "module_dependency_reference_set_expanded_view;",
            "REFRESH MATERIALIZED VIEW "
            "description_format_reference_set_expanded_view;"
        ], process_count=MULTIPROCESSING_POOL_SIZE)

        # This needs the concept_expanded_view already refreshed
        # It cannot be inside the next try...except block ( must run )
        _execute_on_pool(["REFRESH MATERIALIZED VIEW search_content_view;"])

        # These can execute in an embarassingly parallel manner
        # Create indexes after the tables they refer to are populated
        # Refresh the search view when sure concept_expanded_view is refreshed
        try:
            _execute_on_pool([
                "CREATE INDEX concept_expanded_view_concept_id ON "
                "concept_expanded_view(concept_id);",
                "CREATE INDEX concept_expanded_view_id ON "
                "concept_expanded_view(id);"

                "CREATE INDEX description_expanded_view_component_id ON "
                "description_expanded_view(component_id);",
                "CREATE INDEX description_expanded_view_id ON "
                "description_expanded_view(id);",

                "CREATE INDEX relationship_expanded_view_component_id ON "
                "relationship_expanded_view(component_id);",
                "CREATE INDEX relationship_expanded_view_id ON "
                "relationship_expanded_view(id);",

                "CREATE INDEX reference_set_descriptor_row_id ON "
                "reference_set_descriptor_reference_set_expanded_view"
                "(row_id);",
                "CREATE INDEX reference_set_descriptor_refset_id ON "
                "reference_set_descriptor_reference_set_expanded_view"
                "(refset_id);",
                "CREATE INDEX reference_set_descriptor_module_id ON "
                "reference_set_descriptor_reference_set_expanded_view"
                "(module_id);",

                "CREATE INDEX simple_row_id ON "
                "simple_reference_set_expanded_view(row_id);",
                "CREATE INDEX simple_refset_id ON "
                "simple_reference_set_expanded_view(refset_id);",
                "CREATE INDEX simple_module_id ON "
                "simple_reference_set_expanded_view(module_id);",

                "CREATE INDEX ordered_row_id ON "
                "ordered_reference_set_expanded_view(row_id);",
                "CREATE INDEX ordered_refset_id ON "
                "ordered_reference_set_expanded_view(refset_id);",
                "CREATE INDEX ordered_module_id ON "
                "ordered_reference_set_expanded_view(module_id);",

                "CREATE INDEX attribute_value_row_id ON "
                "attribute_value_reference_set_expanded_view(row_id);",
                "CREATE INDEX attribute_value_refset_id ON "
                "attribute_value_reference_set_expanded_view(refset_id);",
                "CREATE INDEX attribute_value_module_id ON "
                "attribute_value_reference_set_expanded_view(module_id);",

                "CREATE INDEX simple_map_row_id ON "
                "simple_map_reference_set_expanded_view(row_id);",
                "CREATE INDEX simple_map_refset_id ON "
                "simple_map_reference_set_expanded_view(refset_id);",
                "CREATE INDEX simple_map_module_id ON "
                "simple_map_reference_set_expanded_view(module_id);",

                "CREATE INDEX complex_map_row_id ON "
                "complex_map_reference_set_expanded_view(row_id);",
                "CREATE INDEX complex_map_refset_id ON "
                "complex_map_reference_set_expanded_view(refset_id);",
                "CREATE INDEX complex_map_module_id ON "
                "complex_map_reference_set_expanded_view(module_id);",

                "CREATE INDEX extended_map_row_id ON "
                "extended_map_reference_set_expanded_view"
                "(row_id);",
                "CREATE INDEX extended_map_refset_id ON "
                "extended_map_reference_set_expanded_view(refset_id);",
                "CREATE INDEX extended_map_module_id ON "
                "extended_map_reference_set_expanded_view(module_id);",

                "CREATE INDEX language_map_row_id ON "
                "language_reference_set_expanded_view(row_id);",
                "CREATE INDEX language_map_refset_id ON "
                "language_reference_set_expanded_view(refset_id);",
                "CREATE INDEX language_map_module_id ON "
                "language_reference_set_expanded_view(module_id);",

                "CREATE INDEX query_specification_row_id ON "
                "query_specification_reference_set_expanded_view(row_id);",
                "CREATE INDEX query_specification_refset_id ON "
                "query_specification_reference_set_expanded_view(refset_id);",
                "CREATE INDEX query_specification_module_id ON "
                "query_specification_reference_set_expanded_view(module_id);",

                "CREATE INDEX annotation_map_row_id ON "
                "annotation_reference_set_expanded_view(row_id);",
                "CREATE INDEX annotation_map_refset_id ON "
                "annotation_reference_set_expanded_view(refset_id);",
                "CREATE INDEX annotation_map_module_id ON "
                "annotation_reference_set_expanded_view(module_id);",

                "CREATE INDEX association_map_row_id ON "
                "association_reference_set_expanded_view(row_id);",
                "CREATE INDEX association_map_refset_id ON "
                "association_reference_set_expanded_view(refset_id);",
                "CREATE INDEX association_map_module_id ON "
                "association_reference_set_expanded_view(module_id);",

                "CREATE INDEX module_dependency_map_row_id ON "
                "module_dependency_reference_set_expanded_view(row_id);",
                "CREATE INDEX module_dependency_map_refset_id ON "
                "module_dependency_reference_set_expanded_view(refset_id);",
                "CREATE INDEX module_dependency_map_module_id ON "
                "module_dependency_reference_set_expanded_view(module_id);",

                "CREATE INDEX description_format_map_row_id ON "
                "description_format_reference_set_expanded_view(row_id);",
                "CREATE INDEX description_format_map_refset_id ON "
                "description_format_reference_set_expanded_view(refset_id);",
                "CREATE INDEX description_format_map_module_id ON "
                "description_format_reference_set_expanded_view(module_id);"
            ], process_count=MULTIPROCESSING_POOL_SIZE)
        except psycopg2.ProgrammingError:
            LOGGER.debug('Looks like we already had indexes; '
                         'normal when refreshing on an existing database')


def refresh_dynamic_snapshot():
    """Dynamically create a 'most recent snapshot' view"""
    with transaction.atomic():
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
            "REFRESH MATERIALIZED VIEW "
            "snomed_query_specification_reference_set;",
            "REFRESH MATERIALIZED VIEW snomed_annotation_reference_set;",
            "REFRESH MATERIALIZED VIEW snomed_association_reference_set;",
            "REFRESH MATERIALIZED VIEW "
            "snomed_module_dependency_reference_set;",
            "REFRESH MATERIALIZED VIEW "
            "snomed_description_format_reference_set;"
        ], process_count=MULTIPROCESSING_POOL_SIZE)


def load_release_files(path_dict):
    """Take a dict from discover.py->enumerate_release_files & trigger db load

    :param path_dict:
    """
    with transaction.atomic():
        # Because we do not have FKs, we can parallelize everything
        LOGGER.debug('Starting the SNOMED raw data load...')
        _execute_map_on_pool({
            load_concepts: path_dict["CONCEPTS"],
            load_descriptions: path_dict["DESCRIPTIONS"],
            load_relationships: path_dict["RELATIONSHIPS"],
            load_text_definitions: path_dict["TEXT_DEFINITIONS"],
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
        }, process_count=MULTIPROCESSING_POOL_SIZE)
        LOGGER.debug('Finished the SNOMED raw data load')

        # Now create the indexes
        LOGGER.debug('About to create source table indexes...')
        _create_source_table_indexes()
        LOGGER.debug('Created source table indexes')
