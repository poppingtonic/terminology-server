"""Dynamic snapshot views ( most recent snapshot ) for the core models"""
from django.db import models
from .shared import Component

class ConceptDynamicSnapshot(Component):
    """Concepts that are current as at the release of the latest SNOMED release"""
    definition_status_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_concept'


class DescriptionDynamicSnapshot(Component):
    """Descriptions that are current as at the release of the latest SNOMED release"""
    concept_id = models.BigIntegerField()
    language_code = models.CharField(max_length=2, default='en')
    type_id = models.BigIntegerField()
    case_significance_id = models.BigIntegerField()
    term = models.TextField()

    class Meta:
        managed = False
        db_table = 'snomed_description'


class RelationshipDynamicSnapshot(Component):
    """Relationships that are current as at the release of the latest SNOMED release"""
    source_id = models.BigIntegerField()
    destination_id = models.BigIntegerField()
    relationship_group = models.PositiveSmallIntegerField(default=0)
    type_id = models.BigIntegerField()
    characteristic_type_id = models.BigIntegerField()
    modifier_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_relationship'
