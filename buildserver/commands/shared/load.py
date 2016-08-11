# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import

import multiprocessing
import os
import shutil
import logging
import contextlib
import wrapt
from sqlalchemy import text
from sil_snomed_server.app import db
from sil_snomed_server.config.config import basedir

from sarge import run
from collections import Iterable
from datetime import datetime

LOGGER = logging.getLogger(__name__)
MULTIPROCESSING_POOL_SIZE = multiprocessing.cpu_count()

def _sqlalchemy_connection():
    return db.session.connection().connection

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


def _strip_first_line(source_file_path):
    """
    Discard the header row before loading the data.
    Makes a backup file 'source_file_path.bak'.
    """
    run("sed -i.bak -e '1d' {}".format(source_file_path))
    run("head -1 {}".format(source_file_path))
    return source_file_path  # Should exist from here

    # Exiting from here is a bug
    raise Exception('Unable to rewrite %s' % source_file_path)


def _confirm_param_is_an_iterable(param):
    """Used below to enforce the invariant that the param should be a list"""
    if not isinstance(param, Iterable):
        raise Exception('Expected an iterable')


def _load(table_name, file_path_list, cols):
    """The actual worker method that reads the data into the database"""
    _confirm_param_is_an_iterable(file_path_list)
    conn = _sqlalchemy_connection()
    cursor = conn.cursor()

    for file_path in file_path_list:
        rewritten_file = _strip_first_line(file_path)
        try:
            with open(rewritten_file) as rewrite:
                cursor.copy_from(
                    rewrite, table_name, size=32768, columns=cols)
                cursor.execute('ANALYZE {};'.format(table_name))
                conn.commit()
            # Now restore the file (reduces space used by half!)
            os.rename(file_path + '.bak', file_path)
        except Exception as exception:
            os.rename(file_path + '.bak', file_path)
            print("Unable to load data from file: {}. Exception: {}".
                  format(file_path, exception))


def _execute_and_commit(statement, view_name=None):
    """Execute an SQL statement; used to parallelize view refereshes"""
    with _sqlalchemy_connection() as conn:
        with conn.begin() as trans:
            trans.execute(statement)
            if view_name:
              cur.execute('ANALYZE {};'.format(view_name))
        trans.commit()


def execute_map_on_pool(callable_input_map,
                        process_count=MULTIPROCESSING_POOL_SIZE):
    """The obvious choice ( Pool ) has not been used because it does not play
    well with our performance measuring decorator

    :param: callable_input_map
    """
    processes = [
        multiprocessing.Process(target=fn, args=(inp,) if inp is not None else ())
        for fn, inp in iter(callable_input_map.items())
    ]
    for p in processes:
      p.start()
    for p in processes:
      p.join()


def load_concepts(file_path_list):
    """Load concepts from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_concept_f', file_path_list,
          ['id', 'effective_time', 'active',
           'module_id', 'definition_status_id'])


def load_descriptions(file_path_list):
    """Load descriptions from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_description_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id',
           'concept_id', 'language_code', 'type_id', 'term',
           'case_significance_id'])


def load_relationships(file_path_list):
    """Load relationships from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_relationship_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id',
           'source_id', 'destination_id', 'relationship_group', 'type_id',
           'characteristic_type_id', 'modifier_id'])


def load_text_definitions(file_path_list):
    """Delegate to the description loading logic
    :param file_path_list:
    """
    load_descriptions(file_path_list)


def load_simple_reference_sets(file_path_list):
    """Load simple reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_simplerefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id'])


def load_ordered_reference_sets(file_path_list):
    """Load ordered reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_orderedrefset_full', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', '"order"', 'linked_to_id'])


def load_attribute_value_reference_sets(file_path_list):
    """Load attribute value reference set from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_attributevaluerefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'value_id'])


def load_simple_map_reference_sets(file_path_list):
    """Load simple map reference sets from RF2 distribution file

    :param file_path_list:
    """
    _load('curr_simplemaprefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_target'])


def load_complex_map_int_reference_sets(file_path_list):
    """Load complex map reference sets from RF2 distribution files

    :param file_path_list:
    """
    _load('curr_complexmaprefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id'])


def load_complex_map_gb_reference_sets(file_path_list):
    """Like for INTernational above, but with an extra map_block column

    For United Kingdom SNOMED->OPCS and SNOMED->ICD 10 maps
    """
    _load('curr_complexmaprefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_block'])


def load_extended_map_reference_sets(file_path_list):
    """Load extended map reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_extendedmaprefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'map_group', 'map_priority', 'map_rule',
           'map_advice', 'map_target', 'correlation_id', 'map_category_id'])


def load_language_reference_sets(file_path_list):
    """Load language reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_langrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'acceptability_id'])


def load_query_specification_reference_sets(file_path_list):
    """
    Load query specification reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_queryspecificationrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'query'])


def load_annotation_reference_sets(file_path_list):
    """Load annotation reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_annotationrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'annotation'])


def load_association_reference_sets(file_path_list):
    """Load association reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_associationrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'target_component_id'])


def load_module_dependency_reference_sets(file_path_list):
    """Load module dependency reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_moduledependencyrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'source_effective_time',
           'target_effective_time'])


def load_description_format_reference_sets(file_path_list):
    """Load description format reference sets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_descriptionformatrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'description_format_id',
           'description_length'])


def load_refset_descriptor_reference_sets(file_path_list):
    """Load refset descriptor refsets from the RF2 distribution file

    :param file_path_list:
    """
    _load('curr_referencesetdescriptorrefset_f', file_path_list,
          ['id', 'effective_time', 'active', 'module_id', 'refset_id',
           'referenced_component_id', 'attribute_description_id',
           'attribute_type_id', 'attribute_order'])


def load_description_type_reference_sets(file_path_list):
    """Delegate to the description format reference set loader
    :param file_path_list:
    """
    load_description_format_reference_sets(file_path_list)

def run_file(filename):
    """
    Run sql statements in a file
    :param filename of the file with sql statements
    :return a list of ResultProxy objects (results from each of
    the sql statements being run)
    """
    conn = _sqlalchemy_connection()
    cursor = conn.cursor()

    with open(filename, "r") as query_file:
        queries = query_file.read().replace("\n", "").split(";")
        queries = [q.strip() for q in queries]
        queries = [q for q in queries if q != '']
        for query in queries:
            print(">> {}".format(query))
            cursor.execute(query)
            conn.commit()

def make_current_snapshot():
    snapshot_script = os.path.join(basedir, 'migrations/sql/snapshot.sql')
    run_file(snapshot_script)

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

    make_current_snapshot()
