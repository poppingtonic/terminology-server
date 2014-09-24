# coding=utf-8
"""Translate between JSON and the terminology server's data model"""
from rest_framework import serializers
from rest_framework import pagination
from rest_framework import status
from rest_framework.exceptions import APIException

from core.models import (
    ConceptDenormalizedView, ConceptFull,
    DescriptionDenormalizedView, DescriptionFull,
    RelationshipDenormalizedView, RelationshipFull
)
from refset.models import (
    SimpleReferenceSetDenormalizedView,
    SimpleReferenceSetFull,
    OrderedReferenceSetDenormalizedView,
    OrderedReferenceSetFull,
    AttributeValueReferenceSetDenormalizedView,
    AttributeValueReferenceSetFull,
    SimpleMapReferenceSetDenormalizedView,
    SimpleMapReferenceSetFull,
    ComplexMapReferenceSetDenormalizedView,
    ComplexMapReferenceSetFull,
    ExtendedMapReferenceSetDenormalizedView,
    ExtendedMapReferenceSetFull,
    LanguageReferenceSetDenormalizedView,
    LanguageReferenceSetFull,
    QuerySpecificationReferenceSetDenormalizedView,
    QuerySpecificationReferenceSetFull,
    AnnotationReferenceSetDenormalizedView,
    AnnotationReferenceSetFull,
    AssociationReferenceSetDenormalizedView,
    AssociationReferenceSetFull,
    ModuleDependencyReferenceSetDenormalizedView,
    ModuleDependencyReferenceSetFull,
    DescriptionFormatReferenceSetDenormalizedView,
    DescriptionFormatReferenceSetFull,
    ReferenceSetDescriptorReferenceSetDenormalizedView,
    ReferenceSetDescriptorReferenceSetFull
)

from .fields import JSONField


class TerminologySerializerException(APIException):
    """Communicate errors that arise from wrong input to serializers"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Serialization / deserialization error'


def _confirm_concept_descends_from(concept_id, candidate_parent_id):
    """A helper; used extensively by validators in the serializers below"""
    try:
        return concept_id in ConceptDenormalizedView.objects.get(
            concept_id=candidate_parent_id).is_a_children_ids
    except ConceptDenormalizedView.DoesNotExist:
        raise TerminologySerializerException(
            'There is no denormalized view entry for concept %s ( testing for '
            'it as a candidate parent of %s )' %
            (concept_id, candidate_parent_id)
        )


def _confirm_concept_exists(concept_id):
    """Another helper; used by the validators below"""
    try:
        # Note that we use the "raw" model ( not the materialized view )
        return ConceptFull.objects.get(concept_id=concept_id)
    except ConceptDenormalizedView.DoesNotExist:
        raise TerminologySerializerException(
            'There is no denormalized view entry for concept %s ' % concept_id)


class ConceptReadFullSerializer(serializers.ModelSerializer):
    descriptions = JSONField()
    preferred_terms = JSONField()
    synonyms = JSONField()

    is_a_parents = JSONField()
    is_a_children = JSONField()
    is_a_direct_parents = JSONField()
    is_a_direct_children = JSONField()

    part_of_parents = JSONField()
    part_of_children = JSONField()
    part_of_direct_parents = JSONField()
    part_of_direct_children = JSONField()

    other_parents = JSONField()
    other_children = JSONField()
    other_direct_parents = JSONField()
    other_direct_children = JSONField()

    class Meta:
        model = ConceptDenormalizedView


class ConceptReadShortenedSerializer(serializers.ModelSerializer):
    preferred_terms = JSONField(source='preferred_terms_list_shortened')
    synonyms = JSONField(source='synonyms_list_shortened')

    is_a_direct_parents = JSONField()
    is_a_direct_children = JSONField()

    class Meta:
        model = ConceptDenormalizedView
        fields = (
            'concept_id',
            'preferred_terms', 'synonyms',
            'is_a_direct_parents', 'is_a_direct_children'
        )


class ConceptPaginationSerializer(pagination.PaginationSerializer):
    """
    Serialized concepts, for the list API
    """
    class Meta:
        object_serializer_class = ConceptReadShortenedSerializer


class ConceptSubsumptionSerializer(serializers.ModelSerializer):
    is_a_direct_parents = JSONField(source='is_a_direct_parents')
    is_a_parents = JSONField(source='is_a_parents')
    is_a_direct_children = JSONField(source='is_a_direct_children')
    is_a_children = JSONField(source='is_a_children')

    class Meta:
        model = ConceptDenormalizedView
        fields = (
            'is_a_parents', 'is_a_children',
            'is_a_direct_parents', 'is_a_direct_children'
        )


class ComponentWriteBaseSerializer(serializers.ModelSerializer):
    """Hold shared validators ( for all component write serializers )"""
    def validate_module_id(self, attrs, source):
        """All modules descend from 900000000000443000"""
        _confirm_concept_descends_from(attrs[source], 900000000000443000)
        return attrs


class ConceptWriteSerializer(ComponentWriteBaseSerializer):
    """Support writing to the concept 'source' SNOMED concept table"""

    def validate_definition_status_id(self, attrs, source):
        """The definition status should descend from 900000000000444006"""
        _confirm_concept_descends_from(attrs[source], 900000000000444006)
        return attrs

    class Meta:
        model = ConceptFull


class DescriptionReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = DescriptionDenormalizedView


class DescriptionPaginationSerializer(pagination.PaginationSerializer):
    """
    Serialized descriptions, for the list API
    """
    class Meta:
        object_serializer_class = DescriptionReadSerializer


class DescriptionWriteSerializer(ComponentWriteBaseSerializer):
    """Support writing to the description 'source' SNOMED concept table"""

    def validate_type_id(self, attrs, source):
        """Should be a descendant of 900000000000446008"""
        _confirm_concept_descends_from(attrs[source], 900000000000446008)
        return attrs

    def validate_case_significance_id(self, attrs, source):
        """Should be a descendant of 900000000000447004"""
        _confirm_concept_descends_from(attrs[source], 900000000000447004)
        return attrs

    def validate_concept_id(self, attrs, source):
        """Check that the concept_id exists"""
        _confirm_concept_exists(attrs[source])
        return attrs

    def validate_term(self, attrs, source):
        """The term length must be less than 32768

        This particular validator is naive. A proper implementation would:

         * determine what reference set descriptor applies to the description
           that is to be edited
         * use values stored in that descriptor to validate both the length
           and format of the terms

        This particular validation is at the time of writing not deemed to be
        "important enough" to merit that level of effort.
        """
        if len(attrs[source]) > 32768:
            raise TerminologySerializerException(
                'A term longer than 32768 chars has been supplied')
        return attrs

    def validate_language_code(self, attrs, source):
        """The only accepted language code is 'en'"""
        if attrs[source] != 'en':
            raise TerminologySerializerException(
                'The only permitted language code for this server is "en"')
        return attrs

    class Meta:
        model = DescriptionFull


class RelationshipReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationshipDenormalizedView


class RelationshipPaginationSerializer(pagination.PaginationSerializer):
    """
    Serialized relationships, for the list API
    """
    class Meta:
        object_serializer_class = RelationshipReadSerializer


class RelationshipWriteSerializer(ComponentWriteBaseSerializer):
    """Support writing to the relationships 'source' SNOMED concept table"""

    def validate_type_id(self, attrs, source):
        """Must be set to a descendant of 'Linkage concept [106237007]'"""
        _confirm_concept_descends_from(attrs[source], 106237007)
        return attrs

    def validate_characteristic_type_id(self, attrs, source):
        """Must be set to a descendant of '900000000000449001'"""
        _confirm_concept_descends_from(attrs[source], 900000000000449001)
        return attrs

    def validate_modifier_id(self, attrs, source):
        """Must be set to a descendant of '900000000000450001'"""
        _confirm_concept_descends_from(attrs[source], 900000000000450001)
        return attrs

    def validate_source_id(self, attrs, source):
        """The source_id must exist"""
        _confirm_concept_exists(attrs[source])
        return attrs

    def validate_destination_id(self, attrs, source):
        """The destination id must exist"""
        _confirm_concept_exists(attrs[source])
        return attrs

    class Meta:
        model = RelationshipFull


class SimpleReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleReferenceSetDenormalizedView


class SimpleReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = SimpleReferenceSetReadSerializer


class RefsetWriteBaseSerializer(serializers.ModelSerializer):
    """Home for validations shared by different refset write seriaizers"""

    def validate_module_id(self, attrs, source):
        """All modules descend from 900000000000443000"""
        _confirm_concept_descends_from(attrs[source], 900000000000443000)
        return attrs


class SimpleReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '446609009' """
        _confirm_concept_descends_from(attrs[source], 446609009)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = SimpleReferenceSetFull


class OrderedReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedReferenceSetDenormalizedView


class OrderedReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = OrderedReferenceSetReadSerializer


class OrderedReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '447258008' """
        _confirm_concept_descends_from(attrs[source], 447258008)
        return attrs

    def validate_linked_to_id(self, attrs, source):
        """The component that is linked to should exist"""
        _confirm_concept_exists(attrs[source])
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = OrderedReferenceSetFull


class AttributeValueReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeValueReferenceSetDenormalizedView


class AttributeValueReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AttributeValueReferenceSetReadSerializer


class AttributeValueReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000480006'"""
        _confirm_concept_descends_from(attrs[source], 900000000000480006)
        return attrs

    def validate_value_id(self, attrs, source):
        """Check that the value_id exists"""
        _confirm_concept_exists(attrs[source])
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = AttributeValueReferenceSetFull


class SimpleMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleMapReferenceSetDenormalizedView


class SimpleMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = SimpleMapReferenceSetReadSerializer


class SimpleMapReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000496009' """
        _confirm_concept_descends_from(attrs[source], 900000000000496009)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = SimpleMapReferenceSetFull


class ComplexMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplexMapReferenceSetDenormalizedView


class ComplexMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ComplexMapReferenceSetReadSerializer


class ComplexExtendedMapBaseWriteSerializer(RefsetWriteBaseSerializer):
    """Home for validations shared between complex and extended maps"""

    def validate_correlation_id(self, attrs, source):
        """Must descend from '447247004 - Map correlation value'"""
        _confirm_concept_descends_from(attrs[source], 447247004)
        return attrs


class ComplexMapReferenceSetWriteSerializer(
        ComplexExtendedMapBaseWriteSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '447250001' """
        _confirm_concept_descends_from(attrs[source], 447250001)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = ComplexMapReferenceSetFull


class ExtendedMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtendedMapReferenceSetDenormalizedView


class ExtendedMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ExtendedMapReferenceSetReadSerializer


class ExtendedMapReferenceSetWriteSerializer(
        ComplexExtendedMapBaseWriteSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '609331003' """
        _confirm_concept_descends_from(attrs[source], 609331003)
        return attrs

    def validate_map_category_id(self, attrs, source):
        """Should descend from 'Concept: [609330002]  Map category value'"""
        _confirm_concept_descends_from(attrs[source], 609330002)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = ExtendedMapReferenceSetFull


class LanguageReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageReferenceSetDenormalizedView


class LanguageReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = LanguageReferenceSetReadSerializer


class LanguageReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000506000' """
        _confirm_concept_descends_from(attrs[source], 900000000000506000)
        return attrs

    def validate_acceptability_id(self, attrs, source):
        """Must descend from 'Concept: [900000000000511003]  Acceptability' """
        _confirm_concept_descends_from(attrs[source], 900000000000511003)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = LanguageReferenceSetFull


class QuerySpecificationReferenceSetReadSerializer(
        serializers.ModelSerializer):

    class Meta:
        model = QuerySpecificationReferenceSetDenormalizedView


class QuerySpecificationReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = QuerySpecificationReferenceSetReadSerializer


class QuerySpecificationReferenceSetWriteSerializer(
        RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000512005' """
        _confirm_concept_descends_from(attrs[source], 900000000000512005)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = QuerySpecificationReferenceSetFull


class AnnotationReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnotationReferenceSetDenormalizedView


class AnnotationReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AnnotationReferenceSetReadSerializer


class AnnotationReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000516008' """
        _confirm_concept_descends_from(attrs[source], 900000000000516008)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = AnnotationReferenceSetFull


class AssociationReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssociationReferenceSetDenormalizedView


class AssociationReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AssociationReferenceSetReadSerializer


class AssociationReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000521006' """
        _confirm_concept_descends_from(attrs[source], 900000000000521006)
        return attrs

    def validate_target_component_id(self, attrs, source):
        """Ensure target_component_id exists and is of the correct type"""
        pass

    def validate_referenced_component_id(self, attrs, source):
        pass

    class Meta:
        model = AssociationReferenceSetFull


class ModuleDependencyReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModuleDependencyReferenceSetDenormalizedView


class ModuleDependencyReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ModuleDependencyReferenceSetReadSerializer


class ModuleDependencyReferenceSetWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000534007' """
        _confirm_concept_descends_from(attrs[source], 900000000000534007)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        """Must refer to a concept which is a child of '900000000000443000'"""
        _confirm_concept_descends_from(attrs[source], 900000000000443000)
        return attrs

    class Meta:
        model = ModuleDependencyReferenceSetFull


class DescriptionFormatReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = DescriptionFormatReferenceSetDenormalizedView


class DescriptionFormatReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = DescriptionFormatReferenceSetReadSerializer


class DescriptionFormatReferenceSetWriteSerializer(
        RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000538005' """
        _confirm_concept_descends_from(attrs[source], 900000000000538005)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        """Must be a descendant of "Description Type" (900000000000446008) """
        _confirm_concept_descends_from(attrs[source], 900000000000446008)
        return attrs

    def validate_description_format_id(self, attrs, source):
        """Must descend from 'Concept: [900000000000539002]'"""
        _confirm_concept_descends_from(attrs[source], 900000000000539002)
        return attrs

    class Meta:
        model = DescriptionFormatReferenceSetFull


class ReferenceSetDescriptorReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferenceSetDescriptorReferenceSetDenormalizedView


class ReferenceSetDescriptorPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ReferenceSetDescriptorReadSerializer


class ReferenceSetDescriptorWriteSerializer(RefsetWriteBaseSerializer):

    def validate_refset_id(self, attrs, source):
        """Should be a descendant of '900000000000456007' """
        _confirm_concept_descends_from(attrs[source], 900000000000456007)
        return attrs

    def validate_referenced_component_id(self, attrs, source):
        pass  # TODO Add a docstring that makes sense too

    def validate_attribute_description_id(self, attrs, source):
        pass  # TODO Add a docstring that makes sense too

    def validate_attribute_type_id(self, attrs, source):
        pass  # TODO Add a docstring that makes sense too

    class Meta:
        model = ReferenceSetDescriptorReferenceSetFull
