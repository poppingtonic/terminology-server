import logging
import re

from django.db import models
from django.core.exceptions import ValidationError


LOGGER = logging.getLogger(__name__)


class CustomDjangoFieldValidationError(ValidationError):
    pass


def _check_if_wrapped_in_parentheses(value):
    """Return True if the value string is wrapped in ()"""
    pass

    raise CustomDjangoFieldValidationError(
        'Expected %s to be wrapped in ()' % value)


def _check_if_wrapped_in_braces(value):
    """Return True if the value string is wrapped in {}"""
    pass

    raise CustomDjangoFieldValidationError(
        'Expected %s to be wrapped in {}' % value)


def _extract_tuple_from_string(value):
    """Parse the contents into a tuple"""
    pass


def _extract_list_from_string(value):
    """Parse the contents into a list"""
    pass


def _map_tuple_to_denormalized_description(input_tuple):
    """A tuple goes in, a dict ( with appropriate value types ) goes out"""
    pass


def _map_tuple_to_expanded_relationship(input_tuple):
    """A tuple goes in, a dict ( with appropriate value types ) goes out"""
    pass


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

    def to_python(self, value):
        """Convert the database representation to a dict"""
        LOGGER.debug(
            "Denormalized description field source value: %s ( %s )" %
            (value, type(value))
        )
        _check_if_wrapped_in_parentheses(value)
        content_tuple = _extract_tuple_from_string(value)
        return _map_tuple_to_denormalized_description(content_tuple)


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

    def to_python(self, value):
        """Convert the database representation to a dict"""
        LOGGER.debug(
            "Denormalized description array field source value: %s ( %s )" %
            (value, type(value))
        )
        _check_if_wrapped_in_braces(value)
        items = _extract_list_from_string(value)
        return [_map_tuple_to_denormalized_description(item) for item in items]


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

    def to_python(self, value):
        """Convert the database representation to a dict"""
        LOGGER.debug(
            "Expanded relationship field source value: %s ( %s )" %
            (value, type(value))
        )
        _check_if_wrapped_in_braces(value)
        items = _extract_list_from_string(value)
        return [_map_tuple_to_expanded_relationship(item) for item in items]
