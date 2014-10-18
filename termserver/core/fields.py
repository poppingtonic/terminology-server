from django.db import models
from psycopg2.extras import register_composite, CompositeCaster

from administration.management.commands.shared.load \
    import _acquire_psycopg2_connection


class DictComposite(CompositeCaster):
    """Composite types come as dicts, not namedtuples"""
    def make(self, values):
        return dict(zip(self.attnames, values))

with _acquire_psycopg2_connection() as conn:
    register_composite('denormalized_description', conn, globally=True,
                       factory=DictComposite)
    register_composite('expanded_relationship', conn, globally=True,
                       factory=DictComposite)


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
