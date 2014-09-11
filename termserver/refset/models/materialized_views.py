# -coding=utf-8
"""Denormalized views used to power refset list APIs"""
from django.db import models
from django_extensions.db.fields import PostgreSQLUUIDField


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
