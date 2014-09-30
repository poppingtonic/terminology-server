# -coding=utf-8
"""Models for SNOMED extension ( refset ) content"""
from django.db import models
from django_extensions.db.fields import PostgreSQLUUIDField


class RefsetBase(models.Model):
    """Abstract base model for all reference set types"""
    row_id = PostgreSQLUUIDField(auto=False)
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()
    refset_id = models.BigIntegerField()
    referenced_component_id = models.BigIntegerField()

    # Used by the editing tools to mark the components that have changed
    pending_rebuild = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ComplexExtendedMapReferenceSetBase(RefsetBase):
    """Shared base class for both complex and extended reference sets"""
    map_group = models.IntegerField()
    map_priority = models.IntegerField()
    map_rule = models.TextField()
    map_advice = models.TextField()
    map_target = models.CharField(max_length=256)
    correlation_id = models.BigIntegerField()

    class Meta:
        abstract = True


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


class SimpleMapReferenceSetFull(RefsetBase):
    """Used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256)

    class Meta:
        db_table = 'snomed_simple_map_reference_set_full'


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


class SimpleReferenceSetDynamicSnapshot(RefsetBase):
    """Currently 'in force' rows of the simple reference sets"""

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
    """Currently 'in force' rows of the simple map reference sets"""
    map_target = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'snomed_simple_map_reference_set'
        verbose_name = 'simple_map_refset_snapshot'


class ComplexMapReferenceSetDynamicSnapshot(
        ComplexExtendedMapReferenceSetBase):
    """Currently 'in force' rows of the complex map reference sets"""
    map_block = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'snomed_complex_map_reference_set'
        verbose_name = 'complex_map_refset_snapshot'


class ExtendedMapReferenceSetDynamicSnapshot(
        ComplexExtendedMapReferenceSetBase):
    """Like for complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_extended_map_reference_set'
        verbose_name = 'extended_map_refset_snapshot'


class LanguageReferenceSetDynamicSnapshot(RefsetBase):
    """Currently 'in force' rows of the language reference sets"""
    acceptability_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_language_reference_set'
        verbose_name = 'language_map_refset_snapshot'


class QuerySpecificationReferenceSetDynamicSnapshot(RefsetBase):
    """Currently 'in force' rows of the query specification reference sets"""
    query = models.TextField()

    class Meta:
        managed = False
        db_table = 'snomed_query_specification_reference_set'
        verbose_name = 'query_spec_refset_snapshot'


class AnnotationReferenceSetDynamicSnapshot(RefsetBase):
    """Currently 'in force' rows of the annotation reference sets"""
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


class RefsetBaseView(models.Model):
    """Abstract base model for all reference set types"""
    id = models.IntegerField(editable=False, primary_key=True)
    row_id = PostgreSQLUUIDField(editable=False, auto=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        abstract = True


class SimpleReferenceSetDenormalizedView(RefsetBaseView):
    """Simple value sets - no additional fields over base refset type"""

    class Meta:
        managed = False
        db_table = 'simple_reference_set_expanded_view'


class OrderedReferenceSetDenormalizedView(RefsetBaseView):
    """Used to group components"""
    order = models.PositiveSmallIntegerField(editable=False)

    linked_to_id = models.BigIntegerField(editable=False)
    linked_to_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ordered_reference_set_expanded_view'


class AttributeValueReferenceSetDenormalizedView(RefsetBaseView):
    """Used to tag components with values"""
    value_id = models.BigIntegerField(editable=False)
    value_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'attribute_value_reference_set_expanded_view'
        verbose_name = 'attrib_value_refset_view'


class SimpleMapReferenceSetDenormalizedView(RefsetBaseView):
    """Used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256, editable=False)

    class Meta:
        managed = False
        db_table = 'simple_map_reference_set_expanded_view'
        verbose_name = 'simple_map_refset_view'


class ComplexExtendedMapReferenceSetBaseView(RefsetBaseView):
    """Shared base class for both complex and extended reference sets"""
    map_group = models.IntegerField(editable=False)
    map_priority = models.IntegerField(editable=False)
    map_rule = models.TextField(editable=False)
    map_advice = models.TextField(editable=False)
    map_target = models.CharField(max_length=256, editable=False)

    correlation_id = models.BigIntegerField(editable=False)
    correlation_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        abstract = True


class ComplexMapReferenceSetDenormalizedView(
        ComplexExtendedMapReferenceSetBaseView):
    """Represent complex mappings; no additional fields"""
    # Optional, used only by the UK OPCS and ICD mapping fields
    map_block = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'complex_map_reference_set_expanded_view'
        verbose_name = 'complex_map_refset_view'


class ExtendedMapReferenceSetDenormalizedView(
        ComplexExtendedMapReferenceSetBaseView):
    """Like complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()
    map_category_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'extended_map_reference_set_expanded_view'
        verbose_name = 'extended_map_refset_view'


class LanguageReferenceSetDenormalizedView(RefsetBaseView):
    """Supports creatingg of sets of descriptions for a language or dialect"""
    acceptability_id = models.BigIntegerField()
    acceptability_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'language_reference_set_expanded_view'
        verbose_name = 'lang_refset_view'


class QuerySpecificationReferenceSetDenormalizedView(RefsetBaseView):
    """Queries that would be run against SNOMED to generate another refset"""
    query = models.TextField()

    class Meta:
        managed = False
        db_table = 'query_specification_reference_set_expanded_view'
        verbose_name = 'query_spec_refset_view'


class AnnotationReferenceSetDenormalizedView(RefsetBaseView):
    """Allow strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    class Meta:
        managed = False
        db_table = 'annotation_reference_set_expanded_view'
        verbose_name = 'annotation_refset_view'


class AssociationReferenceSetDenormalizedView(RefsetBaseView):
    """Create associations between components e.g historical associations"""
    target_component_id = models.BigIntegerField()
    target_component_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'association_reference_set_expanded_view'
        verbose_name = 'association_refset_view'


class ModuleDependencyReferenceSetDenormalizedView(RefsetBaseView):
    """Specify dependencies between modules"""
    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    class Meta:
        managed = False
        db_table = 'module_dependency_reference_set_expanded_view'
        verbose_name = 'module_dep_refset_view'


class DescriptionFormatReferenceSetDenormalizedView(RefsetBaseView):
    """Provide format and length information for different description types"""
    description_format_id = models.BigIntegerField()
    description_format_name = models.TextField(
        editable=False, null=True, blank=True)
    description_length = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'description_format_reference_set_expanded_view'
        verbose_name = 'desc_format_refset_view'


class ReferenceSetDescriptorReferenceSetDenormalizedView(RefsetBaseView):
    """Provide validation information for reference sets"""
    attribute_description_id = models.BigIntegerField()
    attribute_description_name = models.TextField(
        editable=False, null=True, blank=True)

    attribute_type_id = models.BigIntegerField()
    attribute_type_name = models.TextField(
        editable=False, null=True, blank=True)

    attribute_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'reference_set_descriptor_reference_set_expanded_view'
        verbose_name = 'reference set descriptor refset view'
        verbose_name = 'refset_descriptor_refset_view'
