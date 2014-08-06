__author__ = 'ngurenyaga'
"""UNMANAGED models for MATERIALIZED VIEWS that are used as performance optimizations"""

# -coding=utf-8
"""Models for SNOMED extension ( refset ) content. Similar load time constraints to the core models"""
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
    referenced_component_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        abstract = True


class SimpleReferenceSetView(RefsetBaseView):
    """Simple value sets - no additional fields over base refset type"""

    class Meta(object):
        managed = False
        db_table = 'simple_reference_set_expanded_view'


class OrderedReferenceSetView(RefsetBaseView):
    """Used to group components"""
    order = models.PositiveSmallIntegerField(editable=False)

    linked_to_id = models.BigIntegerField(editable=False)
    linked_to_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'ordered_reference_set_expanded_view'


class AttributeValueReferenceSetView(RefsetBaseView):
    """Used to tag components with values"""
    value_id = models.BigIntegerField(editable=False)
    value_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'attribute_value_reference_set_expanded_view'


class SimpleMapReferenceSetView(RefsetBaseView):
    """Used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256, editable=False)

    class Meta(object):
        managed = False
        db_table = 'simple_map_reference_set_expanded_view'


class ComplexExtendedMapReferenceSetBaseView(RefsetBaseView):
    """Shared base class for both complex and extended reference sets"""
    map_group = models.IntegerField(editable=False)
    map_priority = models.IntegerField(editable=False)
    map_rule = models.TextField(editable=False)
    map_advice = models.TextField(editable=False)
    map_target = models.CharField(max_length=256, editable=False)

    correlation_id = models.BigIntegerField(editable=False)
    correlation_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        abstract = True


class ComplexMapReferenceSetView(ComplexExtendedMapReferenceSetBaseView):
    """Represent complex mappings; no additional fields"""
    # Optional, used only by the UK OPCS and ICD mapping fields
    map_block = models.IntegerField(null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'complex_map_reference_set_expanded_view'


class ExtendedMapReferenceSetView(ComplexExtendedMapReferenceSetBaseView):
    """Like complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()
    map_category_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'extended_map_reference_set_expanded_view'


class LanguageReferenceSetView(RefsetBaseView):
    """Supports the creation of sets of descriptions for a language or dialect"""
    acceptability_id = models.BigIntegerField()
    acceptability_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'language_reference_set_expanded_view'


class QuerySpecificationReferenceSetView(RefsetBaseView):
    """Define queries that would be run against the full content of SNOMED to generate another refset"""
    query = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'query_specification_reference_set_expanded_view'


class AnnotationReferenceSetView(RefsetBaseView):
    """Allow strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'annotation_reference_set_expanded_view'


class AssociationReferenceSetView(RefsetBaseView):
    """Create associations between components e.g historical associations"""
    target_component_id = models.BigIntegerField()
    target_component_name = models.TextField(editable=False, null=True, blank=True)

    class Meta(object):
        managed = False
        db_table = 'association_reference_set_expanded_view'


class ModuleDependencyReferenceSetView(RefsetBaseView):
    """Specify dependencies between modules"""
    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    class Meta(object):
        managed = False
        db_table = 'module_dependency_reference_set_expanded_view'


class DescriptionFormatReferenceSetView(RefsetBaseView):
    """Provide format and length information for different description types"""
    description_format_id = models.BigIntegerField()
    description_format_name = models.TextField(editable=False, null=True, blank=True)
    description_length = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'description_format_reference_set_expanded_view'


class ReferenceSetDescriptorReferenceSetView(RefsetBaseView):
    """Provide validation information for reference sets"""
    attribute_description_id = models.BigIntegerField()
    attribute_description_name = models.TextField(editable=False, null=True, blank=True)

    attribute_type_id = models.BigIntegerField()
    attribute_type_name = models.TextField(editable=False, null=True, blank=True)

    attribute_order = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'reference_set_descriptor_reference_set_expanded_view'
        verbose_name = 'reference set descriptor refset view'

