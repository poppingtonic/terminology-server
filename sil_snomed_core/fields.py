"""See composite type registration in core/apps.py"""
from django.db import models
from rest_framework import serializers

import json
import logging

LOGGER = logging.getLogger(__name__)


class DictField(serializers.Field):
    """Read only field to handle DictFields used in denormalized views"""
    def to_representation(self, obj):
        try:
            l = [json.loads(item) for item in obj]
            LOGGER.debug('Object %s native representation is: %s' % (obj, l))
            return l
        except:
            LOGGER.debug('Unable to load from JSON obj %s' % obj)
            return obj


class DenormalizedDescriptionField(models.Field):
    """Implement Django support for the type with this definition:

    CREATE TYPE denormalized_description AS (
        component_id bigint,
        module_id bigint,
        module_name text,
        type_id bigint,
        type_name text,
        effective_time date,
        case_significance_id bigint,
        case_significance_name text,
        term text,
        language_code character varying(2),
        active boolean,
        acceptability_id bigint,
        acceptability_name text,
        refset_id bigint,
        refset_name text
    );
    """
    description = "Contains all of a description's attributes and their names"

    def db_type(self, connection):
        return 'denormalized_description'


class DenormalizedDescriptionArrayField(models.Field):
    """Implement Django support for arrays of the type with this definition:

    CREATE TYPE denormalized_description AS (
        component_id bigint,
        module_id bigint,
        module_name text,
        type_id bigint,
        type_name text,
        effective_time date,
        case_significance_id bigint,
        case_significance_name text,
        term text,
        language_code character varying(2),
        active boolean,
        acceptability_id bigint,
        acceptability_name text,
        refset_id bigint,
        refset_name text
    );
    """
    description = "Contains all of a description's attributes and their names"

    def db_type(self, connection):
        return 'denormalized_description'


class ExpandedRelationshipField(models.Field):
    """Implement Django support for the type with this definition:


    CREATE TYPE expanded_relationship AS (
        concept_id bigint,
        concept_name text
    );
    """
    description = "A relationship's target component identifier & it's name"

    def db_type(self, connection):
        return 'expanded_relationship'
