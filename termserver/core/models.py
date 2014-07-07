"""Models for core SNOMED components ( refsets excluded )"""
# -coding=utf-8
from django.db import models


class SCTIDField(models.BigIntegerField):
    """SNOMED ID Validation Concerns encapsulated here"""
    description = _("SNOMED CT Identifier")
    # TODO - Only positive integer fields
    # TODO - Fields greater than 10^5
    # TODO - Values less than 10^18
    # TODO - Last digit is a Verhoeff dihedral check digit
    # TODO - Must have 5 components; partition identifier, item identifier, namespace id, check digit
    pass


class Component(models.Model):
    """Fields shared between all components"""
    sctid = SCTIDField()
    effective_time = models.DateField()
    active = models.BooleanField()
    module = models.ForeignKey('Concept')

    # TODO - Only one component with the same id can be active at the same time
    # TODO - Confirm match between component types and SCTIDs
    # TODO - Different validation for different component types; use partition id
    # TODO - default export formatter for effective_time that conforms to SNOMED?
    # TODO - validator for module; that it is a descendant of the module concept

    class Meta(object):
        abstract = True


class Concept(Component):
    """SNOMED concepts"""
    definition_status = models.ForeignKey('self')

    # TODO - Validate that definition status is a child of the correct concept

    class Meta(object):
        db_table = 'snomed_concept'


class Description(Component):
    """SNOMED descriptions"""
    concept = models.ForeignKey(Concept)
    language_code = models.CharField(max_length=2)
    type = models.ForeignKey(Concept)
    case_significance = models.ForeignKey(Concept)
    term = models.TextField()

    # TODO - Language code choices
    # TODO - Validate type id choices
    # TODO - Validate terms ( length )
    # TODO - Validate case significance id choices

    class Meta(object):
        db_table = 'snomed_description'


class Relationship(Component):
    """SNOMED relationships"""
    source = models.ForeignKey(Concept)
    destination = models.ForeignKey(Concept)
    relationship_group = models.PositiveSmallIntegerField(default=0)
    type = models.ForeignKey(Concept)
    characteristic_type = models.ForeignKey(Concept)
    modifier = models.ForeignKey(Concept)

    # TODO - Validate type_id choices
    # TODO - Validate characteristic type choices
    # TODO - Validate modifier choices

    class Meta(object):
        db_table = 'snomed_relationship'
