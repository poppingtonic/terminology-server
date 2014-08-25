# -coding=utf-8
"""Models for SNOMED extension ( refset ) content. Similar load time constraints to the core models"""
from django.db import models
from django.core.exceptions import ValidationError
from .shared import RefsetBase, ComplexExtendedMapReferenceSetBase

# TODO - create a general purpose delegate method to check for descent from a specified ancestor during validation


class SimpleReferenceSetFull(RefsetBase):
    """Simple value sets - no additional fields over base refset type"""

    def _validate_refset(self):
        """Should be a descendant of '446609009' """
        if not SNOMED_TESTER.is_child_of(446609009, self.refset_id):
            raise ValidationError("The refset must be a descendant of '446609009'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(SimpleReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_simple_reference_set_full'


class OrderedReferenceSetFull(RefsetBase):
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
        super(OrderedReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_ordered_reference_set_full'


class AttributeValueReferenceSetFull(RefsetBase):
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
        super(AttributeValueReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_attribute_value_reference_set_full'


class SimpleMapReferenceSetFull(RefsetBase):
    """Used for one to one maps between SNOMED and other code systems"""
    map_target = models.CharField(max_length=256)

    def _validate_refset(self):
        """Should be a descendant of '900000000000496009' """
        if not SNOMED_TESTER.is_child_of(900000000000496009, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000496009'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(SimpleMapReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_simple_map_reference_set_full'


class ComplexMapReferenceSetFull(ComplexExtendedMapReferenceSetBase):
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
        super(ComplexMapReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_complex_map_reference_set_full'


class ExtendedMapReferenceSetFull(ComplexExtendedMapReferenceSetBase):
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
        super(ExtendedMapReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_extended_map_reference_set_full'


class LanguageReferenceSetFull(RefsetBase):
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
        super(LanguageReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_language_reference_set_full'


class QuerySpecificationReferenceSetFull(RefsetBase):
    """Define queries that would be run against the full content of SNOMED to generate another refset"""
    query = models.TextField()

    def _validate_refset(self):
        """Should be a descendant of '900000000000512005' """
        if not SNOMED_TESTER.is_child_of(900000000000512005, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000512005'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(QuerySpecificationReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_query_specification_reference_set_full'


class AnnotationReferenceSetFull(RefsetBase):
    """Allow strings to be associated with a component - for any purpose"""
    annotation = models.TextField()

    def _validate_refset(self):
        """Should be a descendant of '900000000000516008' """
        if not SNOMED_TESTER.is_child_of(900000000000516008, self.refset_id):
            raise ValidationError("The refset must be a descendant of '900000000000516008'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_refset()
        super(AnnotationReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_annotation_reference_set_full'


class AssociationReferenceSetFull(RefsetBase):
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
        super(AssociationReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_association_reference_set_full'


class ModuleDependencyReferenceSetFull(RefsetBase):
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
        super(ModuleDependencyReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_module_dependency_reference_set_full'


class DescriptionFormatReferenceSetFull(RefsetBase):
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
        super(DescriptionFormatReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_description_format_reference_set_full'
        verbose_name = 'description_format_refset_full'


class ReferenceSetDescriptorReferenceSetFull(RefsetBase):
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
        super(ReferenceSetDescriptorReferenceSetFull, self).clean()

    class Meta:
        db_table = 'snomed_reference_set_descriptor_reference_set_full'
        verbose_name = 'refset_descriptor_refset_full'
