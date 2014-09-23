# -coding=utf-8
"""Models for SNOMED extension ( refset ) content"""
from django.db import models
from .shared import RefsetBase, ComplexExtendedMapReferenceSetBase


class SimpleReferenceSetFull(RefsetBase):
    """Simple value sets - no additional fields over base refset type"""

    class Meta:
        db_table = 'snomed_simple_reference_set_full'


class OrderedReferenceSetFull(RefsetBase):
    """Used to group components"""
    order = models.PositiveSmallIntegerField()
    linked_to_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_ordered_reference_set_full'


class AttributeValueReferenceSetFull(RefsetBase):
    """Used to tag components with values"""
    value_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_attribute_value_reference_set_full'


class ComplexMapReferenceSetFull(ComplexExtendedMapReferenceSetBase):
    """Represent complex mappings; no additional fields"""
    # Optional, used only by the UK OPCS and ICD mapping fields
    map_block = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'snomed_complex_map_reference_set_full'


class ExtendedMapReferenceSetFull(ComplexExtendedMapReferenceSetBase):
    """Like complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_extended_map_reference_set_full'


class LanguageReferenceSetFull(RefsetBase):
    """Supports the creation of sets of descriptions for a language/dialect"""
    acceptability_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_language_reference_set_full'


class QuerySpecificationReferenceSetFull(RefsetBase):
    """Define queries to be run against the SNOMED to generate refsets"""
    query = models.TextField()

    class Meta:
        db_table = 'snomed_query_specification_reference_set_full'


class AnnotationReferenceSetFull(RefsetBase):
    """Allow strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    class Meta:
        db_table = 'snomed_annotation_reference_set_full'


class AssociationReferenceSetFull(RefsetBase):
    """Create associations between components e.g historical associations"""
    target_component_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_association_reference_set_full'


class ModuleDependencyReferenceSetFull(RefsetBase):
    """Specify dependencies between modules"""
    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    class Meta:
        db_table = 'snomed_module_dependency_reference_set_full'


class DescriptionFormatReferenceSetFull(RefsetBase):
    """Provide format and length information for different description types"""
    description_format_id = models.BigIntegerField()
    description_length = models.IntegerField()

    class Meta:
        db_table = 'snomed_description_format_reference_set_full'
        verbose_name = 'description_format_refset_full'


class ReferenceSetDescriptorReferenceSetFull(RefsetBase):
    """Provide validation information for reference sets"""
    attribute_description_id = models.BigIntegerField()
    attribute_type_id = models.BigIntegerField()
    attribute_order = models.IntegerField()

    class Meta:
        db_table = 'snomed_reference_set_descriptor_reference_set_full'
        verbose_name = 'refset_descriptor_refset_full'
