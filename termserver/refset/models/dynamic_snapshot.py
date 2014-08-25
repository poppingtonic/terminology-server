# -coding=utf-8
"""Models backed by materialized views, implementing the most recent refset snapshots"""
from django.db import models
from .shared import RefsetBase, ComplexExtendedMapReferenceSetBase


class SimpleReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of Simple value sets - no additional fields over base refset type"""

    class Meta:
        managed = False
        db_table = 'snomed_simple_reference_set'
        verbose_name = 'simple_refset_snapshot'


class OrderedReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset used to group components"""
    order = models.PositiveSmallIntegerField()
    linked_to_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_ordered_reference_set'
        verbose_name = 'ordered_refset_snapshot'


class AttributeValueReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset used to tag components with values"""
    value_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_attribute_value_reference_set'
        verbose_name = 'attribute_value_refset_snapshot'


class SimpleMapReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'snomed_simple_map_reference_set'
        verbose_name = 'simple_map_refset_snapshot'


class ComplexMapReferenceSetDynamicSnapshot(ComplexExtendedMapReferenceSetBase):
    """Dynamic snapshot of refset uepresent complex mappings; no additional fields"""
    map_block = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'snomed_complex_map_reference_set'
        verbose_name = 'complex_map_refset_snapshot'


class ExtendedMapReferenceSetDynamicSnapshot(ComplexExtendedMapReferenceSetBase):
    """Like complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_extended_map_reference_set'
        verbose_name = 'extended_map_refset_snapshot'


class LanguageReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset that supports the creation of sets of descriptions for a language or dialect"""
    acceptability_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_language_reference_set'
        verbose_name = 'language_map_refset_snapshot'


class QuerySpecificationReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset used to define queries that would be run against the full content of SNOMED to generate another refset"""
    query = models.TextField()

    class Meta:
        managed = False
        db_table = 'snomed_query_specification_reference_set'
        verbose_name = 'query_spec_refset_snapshot'


class AnnotationReferenceSetDynamicSnapshot(RefsetBase):
    """Dynamic snapshot of refset that allows strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    class Meta:
        managed = False
        db_table = 'snomed_annotation_reference_set'
        verbose_name = 'annotation_refset_snapshot'


class AssociationReferenceSetDynamicSnapshot(RefsetBase):
    """Create associations between components e.g historical associations"""
    target_component_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_association_reference_set'
        verbose_name = 'association_refset_snapshot'


class ModuleDependencyReferenceSetDynamicSnapshot(RefsetBase):
    """Specify dependencies between modules"""
    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    class Meta:
        managed = False
        db_table = 'snomed_module_dependency_reference_set'
        verbose_name = 'mod_dep_refset_snapshot'


class DescriptionFormatReferenceSetDynamicSnapshot(RefsetBase):
    """Provide format and length information for different description types"""
    description_format_id = models.BigIntegerField()
    description_length = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_description_format_reference_set'
        verbose_name = 'description_format_refset_snapshot'


class ReferenceSetDescriptorReferenceSetDynamicSnapshot(RefsetBase):
    """Provide validation information for reference sets"""
    attribute_description_id = models.BigIntegerField()
    attribute_type_id = models.BigIntegerField()
    attribute_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_reference_set_descriptor_reference_set'
        verbose_name = 'refset_descriptor_refset_snapshot'
