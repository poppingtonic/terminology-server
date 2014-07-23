# -coding=utf-8
"""Models for SNOMED extension ( refset ) content. Similar load time constraints to the core models"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django_extensions.db.fields import PostgreSQLUUIDField

# SNOMED_TESTER = settings.SNOMED_TESTER
# TODO - implement new approach to subsumption
# TODO - create a general purpose delegate method to check for descent from a specified ancestor during validation


class RefsetBase(models.Model):
    """Abstract base model for all reference set types"""
    row_id = PostgreSQLUUIDField(auto=False)
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()
    refset_id = models.BigIntegerField()
    referenced_component_id = models.BigIntegerField()

    # TODO - add validator for module
    # TODO - add validator for refset_id
    # TODO - add validator for referenced_component_id
    # TODO - add check constraints to the database too
    # TODO - add a property that inspects the referenced component id and returns the type of component it is

    def _validate_module(self):
        """All modules descend from 900000000000443000

        DRY violation here ( intentional ).
        """
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.module_id):
            raise ValidationError("The module must be a descendant of '900000000000443000'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_module()
        super(RefsetBase, self).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        self.full_clean()
        super(RefsetBase, self).save(*args, **kwargs)

    class Meta(object):
        abstract = True


class SimpleReferenceSet(RefsetBase):
    """Simple value sets - no additional fields over base refset type"""

    def _validate_refset(self):
        """Should be a descendant of '446609009' """
        if not SNOMED_TESTER.is_child_of(446609009, self.refset_id):
            raise ValidationError("The refset must be a descendant of '446609009'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(SimpleReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_simple_reference_set'


class OrderedReferenceSet(RefsetBase):
    """Used to group components"""
    order = models.PositiveSmallIntegerField()
    linked_to_id = models.BigIntegerField()

    # TODO - add validator for linked_to_id

    def _validate_refset(self):
        """Should be a descendant of '447258008' """
        if not SNOMED_TESTER.is_child_of(447258008, self.refset_id):
            raise ValidationError("The refset must be a descendant of '447258008'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(OrderedReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_ordered_reference_set'


class AttributeValueReferenceSet(RefsetBase):
    """Used to tag components with values"""
    value_id = models.BigIntegerField()

    # TODO - add check for existence of value_id

    def _validate_refset(self):
        """Should be a descendant of '900000000000480006' """
        if not SNOMED_TESTER.is_child_of(900000000000480006, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000480006'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(AttributeValueReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_attribute_value_reference_set'


class SimpleMapReferenceSet(RefsetBase):
    """Used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256)

    def _validate_refset(self):
        """Should be a descendant of '900000000000496009' """
        if not SNOMED_TESTER.is_child_of(900000000000496009, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000496009'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(SimpleMapReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_simple_map_reference_set'


class ComplexExtendedMapReferenceSetBase(RefsetBase):
    """Shared base class for both complex and extended reference sets"""
    map_group = models.IntegerField()
    map_priority = models.IntegerField()
    map_rule = models.TextField()
    map_advice = models.TextField()
    map_target = models.CharField(max_length=256)
    correlation_id = models.BigIntegerField()

    # TODO - add validator to check for presence of correlation_id

    def _validate_correlation(self):
        """Must descend from '447247004 - Map correlation value'"""
        if not SNOMED_TESTER.is_child_of(447247004, self.correlation_id):
            raise ValidationError("The correlation must be a descendant of '447247004'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_correlation()
        super(ComplexExtendedMapReferenceSetBase, self).clean()

    class Meta(object):
        abstract = True


class ComplexMapReferenceSet(ComplexExtendedMapReferenceSetBase):
    """Represent complex mappings; no additional fields"""
    # Optional, used only by the UK OPCS and ICD mapping fields
    map_block = models.IntegerField(null=True, blank=True)

    def _validate_refset(self):
        """Should be a descendant of '447250001' """
        if not SNOMED_TESTER.is_child_of(447250001, self.refset_id):
            raise ValidationError("The refset must be a descendant of '447250001'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(ComplexMapReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_complex_map_reference_set'


class ExtendedMapReferenceSet(ComplexExtendedMapReferenceSetBase):
    """Like complex map refsets, but with one additional field"""
    map_category_id = models.BigIntegerField()

    # TODO - add validator that checks for existence of map_category_id

    def _validate_refset(self):
        """Should be a descendant of '609331003' """
        if not SNOMED_TESTER.is_child_of(609331003, self.refset_id):
            raise ValidationError("The refset must be a descendant of '609331003'")

    def _validate_map_category(self):
        """Should descend from '609331003 - Map category value'"""
        if not SNOMED_TESTER.is_child_of(609331003, self.map_category_id):
            raise ValidationError("The map category must be a descendant of '609331003'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_map_category()
        self._validate_refset()
        super(ExtendedMapReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_extended_map_reference_set'


class LanguageReferenceSet(RefsetBase):
    """Supports the creation of sets of descriptions for a language or dialect"""
    acceptability_id = models.BigIntegerField()

    # TODO - add a validator that checks for existence of acceptability_id

    def _validate_acceptability(self):
        """Must descend from 'Concept: [900000000000511003]  Acceptability' """
        if not SNOMED_TESTER.is_child_of(900000000000511003, self.acceptability_id):
            raise ValidationError("The acceptability must be a descendant of '900000000000511003'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000506000' """
        if not SNOMED_TESTER.is_child_of(900000000000506000, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000506000'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_acceptability()
        self._validate_refset()
        super(LanguageReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_language_reference_set'


class QuerySpecificationReferenceSet(RefsetBase):
    """Define queries that would be run against the full content of SNOMED to generate another refset"""
    query = models.TextField()

    def _validate_refset(self):
        """Should be a descendant of '900000000000512005' """
        if not SNOMED_TESTER.is_child_of(900000000000512005, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000512005'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(QuerySpecificationReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_query_specification_reference_set'


class AnnotationReferenceSet(RefsetBase):
    """Allow strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    def _validate_refset(self):
        """Should be a descendant of '900000000000516008' """
        if not SNOMED_TESTER.is_child_of(900000000000516008, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000516008'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(AnnotationReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_annotation_reference_set'


class AssociationReferenceSet(RefsetBase):
    """Create associations between components e.g historical associations"""
    target_component_id = models.BigIntegerField()

    # TODO - add validator that checks for presence of target component id
    # TODO - add property that checks for type of target component id ( share code with a similar one above? )

    def _validate_refset(self):
        """Should be a descendant of '900000000000521006' """
        if not SNOMED_TESTER.is_child_of(900000000000521006, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000521006'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(AssociationReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_association_reference_set'


class ModuleDependencyReferenceSet(RefsetBase):
    """Specify dependencies between modules"""
    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    def _validate_referenced_component(self):
        """Must refer to a concept which is a child of '900000000000443000' ( a module ) """
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.referenced_concept_id):
            raise ValidationError("The referenced concept must be a descendant of '900000000000443000'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000534007' """
        if not SNOMED_TESTER.is_child_of(900000000000534007, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000534007'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_referenced_component()
        self._validate_refset()
        super(ModuleDependencyReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_module_dependency_reference_set'


class DescriptionFormatReferenceSet(RefsetBase):
    """Provide format and length information for different description types"""
    description_format_id = models.BigIntegerField()
    description_length = models.IntegerField()

    # TODO - add property that checks for presence of description format

    def _validate_description_format(self):
        """Must be a child of 'Concept: [900000000000539002]  Description format'"""
        if not SNOMED_TESTER.is_child_of(900000000000539002, self.description_format_id):
            raise ValidationError("The description format must be a descendant of '900000000000539002'")

    def _validate_referenced_component(self):
        """Must refer to a concept which is a child of "Description Type" (900000000000446008) """
        if not SNOMED_TESTER.is_child_of(900000000000446008, self.referenced_concept_id):
            raise ValidationError("The referenced concept must be a descendant of '900000000000446008'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000538005' """
        if not SNOMED_TESTER.is_child_of(900000000000538005, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000538005'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_description_format()
        self._validate_referenced_component()
        self._validate_refset()
        super(DescriptionFormatReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_description_format_reference_set'


class ReferenceSetDescriptorReferenceSet(RefsetBase):
    """Provide validation information for reference sets"""
    attribute_description_id = models.BigIntegerField()
    attribute_type_id = models.BigIntegerField()
    attribute_order = models.IntegerField()

    # TODO - attribute description must be a descendant of 900000000000457003
    # TODO - attribute type must be a descendant of 900000000000459000

    def _validate_referenced_component(self):
        """Must refer to a concept which is a child of "Description Type" (900000000000455006) """
        if not SNOMED_TESTER.is_child_of(900000000000455006, self.referenced_concept_id):
            raise ValidationError("The referenced concept must be a descendant of '900000000000455006'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000456007' """
        if not SNOMED_TESTER.is_child_of(900000000000456007, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000456007'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_referenced_component()
        self._validate_refset()
        super(ReferenceSetDescriptorReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_reference_set_descriptor_reference_set'
