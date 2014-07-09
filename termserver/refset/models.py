# -coding=utf-8
"""Models for SNOMED extension ( refset ) content. Similar load time constraints to the core models"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django_extensions.db.fields import PostgreSQLUUIDField

from core.models import Concept, Relationship, Description

SNOMED_TESTER = settings.SNOMED_TESTER


class RefsetBase(models.Model):
    """Abstract base model for all reference set types"""
    id = PostgreSQLUUIDField(primary_key=True)
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module = models.ForeignKey(Concept, related_name="%(class)s_module")
    refset = models.ForeignKey(Concept, related_name="%(class)s_refset")

    # Ideally, the next three fields should have been a single
    # 'referenced_component' field. But - a Django ORM implementation
    # that would achieve that would require a non-abstract 'Component'
    # base model. The performance and complexity implications of that are
    # unacceptable. Hence this "lightweight denormalization"
    referenced_concept = models.ForeignKey(Concept, null=True, blank=True,
                                           related_name="%(class)s_concept")
    referenced_description = models.ForeignKey(Description, null=True, blank=True,
                                               related_name="%(class)s_description")
    referenced_relationship = models.ForeignKey(Relationship, null=True, blank=True,
                                                related_name='related_name="%(class)s_relationship"')

    @property
    def referenced_component(self):
        """Stand in for the 'referenced_component' field that "should" have been there"""
        if self.referenced_concept:
            return self.referenced_concept
        elif self.referenced_description:
            return self.referenced_description
        elif self.referenced_relationship:
            return self.referenced_relationship

    @property
    def referenced_component_type(self):
        """An aid for client software that uses the 'referenced_component' property"""
        if self.referenced_concept:
            return "CONCEPT"
        elif self.referenced_description:
            return "DESCRIPTION"
        elif self.referenced_relationship:
            return "RELATIONSHIP"

    def _validate_referenced_component(self):
        """Exactly one component should be selected; one of:

         * referenced_component OR
         * referenced_description OR
         * referenced_relationship
        """
        # At least one must be selected
        if (not self.referenced_concept
                and not self.referenced_relationship
                and not self.referenced_description):
            raise ValidationError("At least one component should be selected")

        # Not more than one should be selected
        # Having all three selected is a special case of each of these pairs
        if self.referenced_concept and self.referenced_description:
            raise ValidationError("You cannot reference a concept and a description in the same row")
        if self.referenced_concept and self.referenced_relationship:
            raise ValidationError("You cannot reference a concept and a relationship in the same row")
        if self.referenced_description and self.referenced_relationship:
            raise ValidationError("You cannot reference a description and a relationship in the same row")

    def _validate_module(self):
        """All modules descend from 900000000000443000

        DRY violation here ( intentional ).
        """
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.module.concept_id):
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
        if not SNOMED_TESTER.is_child_of(446609009, self.refset.concept_id):
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
    linked_to = models.ForeignKey(Concept, related_name='ordered_refset_linked_to')

    def _validate_refset(self):
        """Should be a descendant of '447258008' """
        if not SNOMED_TESTER.is_child_of(447258008, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '447258008'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(OrderedReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_ordered_reference_set'


class AttributeValueReferenceSet(RefsetBase):
    """Used to tag components with values"""
    value = models.ForeignKey(Concept, related_name='attribute_value_refset_value')

    def _validate_refset(self):
        """Should be a descendant of '900000000000480006' """
        if not SNOMED_TESTER.is_child_of(900000000000480006, self.refset.concept_id):
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
        if not SNOMED_TESTER.is_child_of(900000000000496009, self.refset.concept_id):
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
    correlation = models.ForeignKey(Concept, related_name="%(class)s_correlation")

    def _validate_correlation(self):
        """Must descend from '447247004 - Map correlation value'"""
        if not SNOMED_TESTER.is_child_of(447247004, self.correlation.concept_id):
            raise ValidationError("The correlation must be a descendant of '447247004'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_correlation()
        super(ComplexExtendedMapReferenceSetBase, self).clean()

    class Meta(object):
        abstract = True


class ComplexMapReferenceSet(ComplexExtendedMapReferenceSetBase):
    """Represent complex mappings; no additional fields"""

    def _validate_refset(self):
        """Should be a descendant of '447250001' """
        if not SNOMED_TESTER.is_child_of(447250001, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '447250001'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(ComplexMapReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_complex_map_reference_set'


class ExtendedMapReferenceSet(ComplexExtendedMapReferenceSetBase):
    """Like complex map refsets, but with one additional field"""
    map_category = models.ForeignKey(Concept, related_name='extended_map_category')

    def _validate_refset(self):
        """Should be a descendant of '609331003' """
        if not SNOMED_TESTER.is_child_of(609331003, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '609331003'")

    def _validate_map_category(self):
        """Should descend from '609331003 - Map category value'"""
        if not SNOMED_TESTER.is_child_of(609331003, self.map_category.concept_id):
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
    acceptability = models.ForeignKey(Concept, related_name='language_reference_set_acceptability')

    def _validate_acceptability(self):
        """Must descend from 'Concept: [900000000000511003]  Acceptability' """
        if not SNOMED_TESTER.is_child_of(900000000000511003, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '900000000000511003'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000506000' """
        if not SNOMED_TESTER.is_child_of(900000000000506000, self.refset.concept_id):
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
        if not SNOMED_TESTER.is_child_of(900000000000512005, self.refset.concept_id):
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
        if not SNOMED_TESTER.is_child_of(900000000000516008, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '900000000000516008'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(AnnotationReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_annotation_reference_set'


class AssociationReferenceSet(RefsetBase):
    """Create associations between components e.g historical associations"""
    # Ideally, the next three fields should have been a single
    # 'target_component' field. But - a Django ORM implementation
    # that would achieve that would require a non-abstract 'Component'
    # base model. The performance and complexity implications of that are
    # unacceptable. Hence this "lightweight denormalization"
    target_concept = models.ForeignKey(Concept, null=True, blank=True,
                                       related_name="association_refset_target_concept")
    target_description = models.ForeignKey(Description, null=True, blank=True,
                                           related_name="association_refset_target_description")
    target_relationship = models.ForeignKey(Relationship, null=True, blank=True,
                                            related_name='association_refset_target_relationship"')

    @property
    def target_component(self):
        """Stand in for the 'target_component' field that "should" have been there"""
        if self.target_concept:
            return self.target_concept
        elif self.target_description:
            return self.target_description
        elif self.target_relationship:
            return self.target_relationship

    @property
    def target_component_type(self):
        """An aid for client software that uses the 'target_component' property"""
        if self.target_concept:
            return "CONCEPT"
        elif self.target_description:
            return "DESCRIPTION"
        elif self.target_relationship:
            return "RELATIONSHIP"

    def _validate_target_component(self):
        """Exactly one component should be selected; one of:

         * target_component OR
         * target_description OR
         * target_relationship
        """
        # At least one must be selected
        if (not self.target_concept
                and not self.target_relationship
                and not self.target_description):
            raise ValidationError("At least one component should be selected as a target")

        # Not more than one should be selected
        # Having all three selected is a special case of each of these pairs
        if self.target_concept and self.target_description:
            raise ValidationError("You cannot reference a concept and a description in the same row")
        if self.target_concept and self.target_relationship:
            raise ValidationError("You cannot reference a concept and a relationship in the same row")
        if self.target_description and self.target_relationship:
            raise ValidationError("You cannot reference a description and a relationship in the same row")

    def _validate_refset(self):
        """Should be a descendant of '900000000000521006' """
        if not SNOMED_TESTER.is_child_of(900000000000521006, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '900000000000521006'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_target_component()
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
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.referenced_concept.concept_id):
            raise ValidationError("The referenced concept must be a descendant of '900000000000443000'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000534007' """
        if not SNOMED_TESTER.is_child_of(900000000000534007, self.refset.concept_id):
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
    description_format = models.ForeignKey(Concept, related_name='description_format_refset_format')
    description_length = models.IntegerField()

    def _validate_description_format(self):
        """Must be a child of 'Concept: [900000000000539002]  Description format'"""
        if not SNOMED_TESTER.is_child_of(900000000000539002, self.description_format.concept_id):
            raise ValidationError("The description format must be a descendant of '900000000000539002'")

    def _validate_referenced_component(self):
        """Must refer to a concept which is a child of "Description Type" (900000000000446008) """
        if not SNOMED_TESTER.is_child_of(900000000000446008, self.referenced_concept.concept_id):
            raise ValidationError("The referenced concept must be a descendant of '900000000000446008'")

    def _validate_refset(self):
        """Should be a descendant of '900000000000538005' """
        if not SNOMED_TESTER.is_child_of(900000000000538005, self.refset.concept_id):
            raise ValidationError("The refset must be a descendant of '900000000000538005'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_description_format()
        self._validate_referenced_component()
        self._validate_refset()
        super(DescriptionFormatReferenceSet, self).clean()

    class Meta(object):
        db_table = 'snomed_description_format_reference_set'
