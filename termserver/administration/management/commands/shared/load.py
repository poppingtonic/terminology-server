# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import
__author__ = 'ngurenyaga'

from django.core.exceptions import ValidationError
from django.conf import settings
from collections import Iterable
from celery import shared_task


import psycopg2
import uuid
import traceback


def _acquire_psycopg2_connection():
    """Relies on default Django settings for database connection parameters"""
    try:
        params = (
            "dbname='%(NAME)s' user='%(USER)s' host='%(HOST)s' password='%(PASSWORD)s' port='%(PORT)s'" %
            settings.DATABASES["default"]
        )
        return psycopg2.connect(params)
    except:
        raise ValidationError("Unable to connect to db with default parameters")


def _strip_first_line(source_file_path):
    """Discard the header row before loading the data"""
    temp_file_name = "/tmp/" + uuid.uuid4().get_hex() + ".tmp"
    with source_file_path.open(mode='rU', encoding='UTF-8') as source:
        with open(temp_file_name, 'w') as dest:
            lines = source.readlines()[1:]
            if lines:
                try:
                    dest.writelines(lines)
                except TypeError as ex:
                    print('Error: %s' % ex)
                    traceback.print_exc()
    return temp_file_name


def _load(table_name, file_path_list, cols):
    """This is the actual worker method that reads the data into the database"""
    _confirm_param_is_an_iterable(file_path_list)
    with _acquire_psycopg2_connection() as conn:
        for file_path in file_path_list:
            with open(_strip_first_line(file_path)) as f:
                with conn.cursor() as cur:
                    cur.copy_from(f, table_name, columns=cols)
        conn.commit()


def _confirm_param_is_an_iterable(param):
    """A helper, used by the methods below to enforce the invariant that their sole parameter should be a list"""
    if not isinstance(param, Iterable):
        raise ValidationError('Expected an iterable')


@shared_task
def load_concepts(file_path_list):
    """
    The top of the concepts distribution file should look like::

        id	effectiveTime	active	moduleId	definitionStatusId
        100001000000107	20040131	0	999000011000000103	900000000000074008
        10001000000102	20040131	1	999000011000000103	900000000000074008
        100011000000109	20040131	0	999000011000000103	900000000000074008

    The database schema looks like this::

        CREATE TABLE snomed_concept
        (
            id serial NOT NULL,
            component_id bigint NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
              definition_status_id bigint NOT NULL,
            CONSTRAINT snomed_concept_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    _load('snomed_concept', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'definition_status_id'])


@shared_task
def load_descriptions(file_path_list):
    """
    The top of the descriptions distribution file should look like::

        id	effectiveTime	active	moduleId	conceptId	languageCode	typeId	term	caseSignificanceId
        2968407015	20140131	1	900000000000207008	697990000	en	900000000000013009	Decreased sense of taste	900000000000020002

    The database schema looks like this::

        CREATE TABLE snomed_description
        (
            id serial NOT NULL,
            component_id bigint NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            concept_id bigint NOT NULL,
            language_code character varying(2) NOT NULL,
            type_id bigint NOT NULL,
            case_significance_id bigint NOT NULL,
            term text NOT NULL,
            CONSTRAINT snomed_description_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    _load('snomed_description', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'concept_id',
           'language_code', 'type_id', 'term', 'case_significance_id'])


@shared_task
def load_relationships(file_path_list):
    pass


@shared_task
def load_text_definitions(file_path_list):
    pass


@shared_task
def load_identifiers(file_path_list):
    pass


@shared_task
def load_stated_relationships(file_path_list):
    pass


@shared_task
def load_simple_reference_sets(file_path_list):
    pass


@shared_task
def load_ordered_reference_sets(file_path_list):
    pass


@shared_task
def load_attribute_value_reference_sets(file_path_list):
    pass


@shared_task
def load_simple_map_reference_sets(file_path_list):
    pass


@shared_task
def load_complex_map_reference_sets(file_path_list):
    pass


@shared_task
def load_extended_map_reference_sets(file_path_list):
    pass


@shared_task
def load_language_reference_sets(file_path_list):
    pass


@shared_task
def load_query_specification_reference_sets(file_path_list):
    pass


@shared_task
def load_annotation_reference_sets(file_path_list):
    pass


@shared_task
def load_association_reference_sets(file_path_list):
    pass


@shared_task
def load_module_dependency_reference_sets(file_path_list):
    pass


@shared_task
def load_description_format_reference_sets(file_path_list):
    pass


@shared_task
def load_refset_descriptor_reference_sets(file_path_list):
    pass


@shared_task
def load_description_type_reference_sets(file_path_list):
    pass


def load_release_files(path_dict):
    """Accept a dict output by discover.py->enumerate_release_files and trigger database loading"""
    load_concepts(path_dict["CONCEPTS"])
    load_descriptions(path_dict["DESCRIPTIONS"])
    load_relationships(path_dict["RELATIONSHIPS"])
    load_text_definitions(path_dict["TEXT_DEFINITIONS"])
    load_stated_relationships(["STATED_RELATIONSHIPS"])
    load_simple_reference_sets(path_dict["SIMPLE_REFERENCE_SET"])
    load_ordered_reference_sets(path_dict["ORDERED_REFERENCE_SET"])
    load_attribute_value_reference_sets(path_dict["ATTRIBUTE_VALUE_REFERENCE_SET"])
    load_simple_map_reference_sets(path_dict["SIMPLE_MAP_REFERENCE_SET"])
    load_complex_map_reference_sets(path_dict["COMPLEX_MAP_REFERENCE_SET"])
    load_extended_map_reference_sets(path_dict["EXTENDED_MAP_REFERENCE_SET"])
    load_language_reference_sets(["LANGUAGE_REFERENCE_SET"])
    load_query_specification_reference_sets(["QUERY_SPECIFICATION_REFERENCE_SET"])
    load_annotation_reference_sets(path_dict["ANNOTATION_REFERENCE_SET"])
    load_association_reference_sets(path_dict["ASSOCIATION_REFERENCE_SET"])
    load_module_dependency_reference_sets(path_dict["MODULE_DEPENDENCY_REFERENCE_SET"])
    load_description_format_reference_sets(path_dict["DESCRIPTION_FORMAT_REFERENCE_SET"])
    load_refset_descriptor_reference_sets(["REFSET_DESCRIPTOR"])
    load_description_type_reference_sets(path_dict["DESCRIPTION_TYPE"])
    load_identifiers(path_dict["IDENTIFIER"])
