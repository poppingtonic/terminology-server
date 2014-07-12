# coding=utf-8
"""The actual loading of SNOMED data into the database"""
from __future__ import absolute_import
__author__ = 'ngurenyaga'

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
            lines = [force_str(source_line) for source_line in source.readlines()[1:]]
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
        2968407015	20140131	1	900000000000207008	697990000	en	900000000000013009	Decr...	900000000000020002

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
    """
    The top of the relationships distribution file should look like::

        id	effectiveTime	active	moduleId	sourceId	destinationId	relationshipGroup	typeId	characteristicTypeId	modifierId
        1000000021	20020131	1	900000000000207008	255116009	367639000	0	308489006	900000000000011006	900000000000451002
        1000000021	20020731	0	900000000000207008	255116009	367639000	0	308489006	900000000000011006	900000000000451002

    The database schema looks like this::

        CREATE TABLE snomed_relationship
        (
            id serial NOT NULL,
            component_id bigint NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            source_id bigint NOT NULL,
            destination_id bigint NOT NULL,
            relationship_group smallint NOT NULL,
            type_id bigint NOT NULL,
            characteristic_type_id bigint NOT NULL,
            modifier_id bigint NOT NULL,
            CONSTRAINT snomed_relationship_pkey PRIMARY KEY (id),
            CONSTRAINT snomed_relationship_relationship_group_check CHECK (relationship_group >= 0)
        )

    :param file_path_list:
    """
    _load('snomed_relationship', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'source_id', 'destination_id',
           'relationship_group', 'type_id', 'characteristic_type_id', 'modifier_id'])


@shared_task
def load_text_definitions(file_path_list):
    """Delegate to the description loading logic
    :param file_path_list:
    """
    load_descriptions(file_path_list)


@shared_task
def load_identifiers(file_path_list):
    """A DELIBERATE no-op
    :param file_path_list:
    """
    print("Identifiers not supported in this server. Unable to load: %s" % [p.name for p in file_path_list])


@shared_task
def load_stated_relationships(file_path_list):
    """A DELIBERATE no-op
    :param file_path_list:
    """
    print("Stated relationships not supported in this server. Unable to load: %s" % [p.name for p in file_path_list])


@shared_task
def load_simple_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        id	effectiveTime	active	moduleId	refsetId	referencedComponentId
        3306012d-5c19-500a-88ec-ae1b6f21bfe5	20110401	1	999000021000000109	999000061000000101	10002003
        4008bbe3-82a8-549b-ab11-c09235629f4b	20110401	1	999000021000000109	999000061000000101	10006000

    The database schema looks like this::

        CREATE TABLE snomed_simple_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            CONSTRAINT snomed_simple_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    _load('snomed_simple_reference_set', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'refset_id', 'referenced_component_id'])


@shared_task
def load_ordered_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        id	effectiveTime	active	moduleId	refsetId	referencedComponentId	order	linkedTo
        165e01be-698d-5850-9a56-8aa573a83425	20040131	1	999000021000000109	999001301000000105	10001000000102	1	0
        165e01be-698d-5850-9a56-8aa573a83425	20131001	0	999000021000000109	999001301000000105	10001000000102	1	0

    The database schema looks like this::

        CREATE TABLE snomed_ordered_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            "order" smallint NOT NULL,
            linked_to_id bigint NOT NULL,
            CONSTRAINT snomed_ordered_reference_set_pkey PRIMARY KEY (id),
            CONSTRAINT snomed_ordered_reference_set_order_check CHECK ("order" >= 0)
        )

    :param file_path_list:
    """
    _load('snomed_ordered_reference_set', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'refset_id', 'referenced_component_id',
           'order', 'linked_to_id'])


@shared_task
def load_attribute_value_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        id	effectiveTime	active	moduleId	refsetId	referencedComponentId	valueId
        <uuid>	20040131	1	999000011000000103	900000000000490003	100001000000111	900000000000495008
        <uuid>	20040131	1	999000011000000103	900000000000490003	10001000000118	900000000000495008

    The database schema looks like this::

        CREATE TABLE snomed_attribute_value_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            value_id bigint NOT NULL,
            CONSTRAINT snomed_attribute_value_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    _load('snomed_attribute_value_reference_set', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'refset_id', 'referenced_component_id', 'value_id'])


@shared_task
def load_simple_map_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        id	effectiveTime	active	moduleId	refsetId	referencedComponentId	mapTarget
        0314672a-f4e5-548d-bb84-f82eac418b99	20140131	1	900000000000207008	446608001	699820000	C76.3
        425999cc-49c2-5e22-9ccd-928963ab1b98	20140131	1	900000000000207008	446608001	699621004	C63.2

    The database schema looks like this::

        CREATE TABLE snomed_simple_map_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            map_target character varying(256) NOT NULL,
            CONSTRAINT snomed_simple_map_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    _load('snomed_simple_map_reference_set', file_path_list,
          ['component_id', 'effective_time', 'active', 'module_id', 'refset_id', 'referenced_component_id',
           'map_target'])


@shared_task
def load_complex_map_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_complex_map_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            map_group integer NOT NULL,
            map_priority integer NOT NULL,
            map_rule text NOT NULL,
            map_advice text NOT NULL,
            map_target character varying(256) NOT NULL,
            correlation_id bigint NOT NULL,
            CONSTRAINT snomed_complex_map_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_extended_map_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_extended_map_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            map_group integer NOT NULL,
            map_priority integer NOT NULL,
            map_rule text NOT NULL,
            map_advice text NOT NULL,
            map_target character varying(256) NOT NULL,
            correlation_id bigint NOT NULL,
            map_category_id bigint NOT NULL,
            CONSTRAINT snomed_extended_map_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_language_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_language_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            acceptability_id bigint NOT NULL,
            CONSTRAINT snomed_language_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_query_specification_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_query_specification_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            query text NOT NULL,
            CONSTRAINT snomed_query_specification_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_annotation_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_annotation_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            annotation text NOT NULL,
            CONSTRAINT snomed_annotation_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_association_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_association_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            target_component_id bigint NOT NULL,
            CONSTRAINT snomed_association_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_module_dependency_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_module_dependency_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            source_effective_time date NOT NULL,
            target_effective_time date NOT NULL,
            CONSTRAINT snomed_module_dependency_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_description_format_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        TODO

    The database schema looks like this::

        CREATE TABLE snomed_description_format_reference_set
        (
            id uuid NOT NULL,
            effective_time date NOT NULL,
            active boolean NOT NULL,
            module_id bigint NOT NULL,
            refset_id bigint NOT NULL,
            referenced_component_id bigint NOT NULL,
            description_format_id bigint NOT NULL,
            description_length integer NOT NULL,
            CONSTRAINT snomed_description_format_reference_set_pkey PRIMARY KEY (id)
        )

    :param file_path_list:
    """
    pass


@shared_task
def load_refset_descriptor_reference_sets(file_path_list):
    """
    The top of the refset distribution file should look like::

        id	effectiveTime	active	moduleId	refsetId	referencedComponentId	attributeDescription	attributeType	attributeOrder
        <uuid>	20050731	1	999000021000000109	900000000000456007	999001121000000104	449608002	900000000000461009	0

    The database schema looks like this::

        TODO

    :param file_path_list:
    """
    pass


@shared_task
def load_description_type_reference_sets(file_path_list):
    """Delegate to the description format reference set loader
    :param file_path_list:
    """
    load_description_format_reference_sets(file_path_list)


@shared_task
def vacuum_database():
    """After the bulk insertions, optimize the tables"""
    with _acquire_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('VACUUM FULL ANALYZE;')


def load_release_files(path_dict):
    """Accept a dict output by discover.py->enumerate_release_files and trigger database loading"""
    # TODO - this would be a great time to refresh the materialized views
    with transaction.atomic():
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

    # Do a full vacuum-analyze immediately after the data load, to optimize query performance
    vacuum_database()
