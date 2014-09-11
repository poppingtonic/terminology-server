# coding=utf-8
"""Translate between JSON and the terminology server's data model"""
from rest_framework import serializers
from rest_framework import pagination

from core.models import (
    ConceptDenormalizedView, ConceptFull,
    DescriptionDenormalizedView, RelationshipDenormalizedView
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


class ConceptWriteSerializer(serializers.ModelSerializer):
    """Support writing to the 'source' SNOMED concept table"""

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


class RelationshipReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationshipDenormalizedView


class RelationshipPaginationSerializer(pagination.PaginationSerializer):
    """
    Serialized relationships, for the list API
    """
    class Meta:
        object_serializer_class = RelationshipReadSerializer


class SimpleReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleReferenceSetDenormalizedView


class SimpleReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = SimpleReferenceSetReadSerializer


class SimpleReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleReferenceSetFull


class OrderedReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedReferenceSetDenormalizedView


class OrderedReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = OrderedReferenceSetReadSerializer


class OrderedReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedReferenceSetFull


class AttributeValueReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeValueReferenceSetDenormalizedView


class AttributeValueReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AttributeValueReferenceSetReadSerializer


class AttributeValueReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeValueReferenceSetFull


class SimpleMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleMapReferenceSetDenormalizedView


class SimpleMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = SimpleMapReferenceSetReadSerializer


class SimpleMapReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SimpleMapReferenceSetFull


class ComplexMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplexMapReferenceSetDenormalizedView


class ComplexMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ComplexMapReferenceSetReadSerializer


class ComplexMapReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplexMapReferenceSetFull


class ExtendedMapReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtendedMapReferenceSetDenormalizedView


class ExtendedMapReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ExtendedMapReferenceSetReadSerializer


class ExtendedMapReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtendedMapReferenceSetFull


class LanguageReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageReferenceSetDenormalizedView


class LanguageReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = LanguageReferenceSetReadSerializer


class LanguageReferenceSetWriteSerializer(serializers.ModelSerializer):

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
        serializers.ModelSerializer):

    class Meta:
        model = QuerySpecificationReferenceSetFull


class AnnotationReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnotationReferenceSetDenormalizedView


class AnnotationReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AnnotationReferenceSetReadSerializer


class AnnotationReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnotationReferenceSetFull


class AssociationReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssociationReferenceSetDenormalizedView


class AssociationReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = AssociationReferenceSetReadSerializer


class AssociationReferenceSetWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssociationReferenceSetFull


class ModuleDependencyReferenceSetReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModuleDependencyReferenceSetDenormalizedView


class ModuleDependencyReferenceSetPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ModuleDependencyReferenceSetReadSerializer


class ModuleDependencyReferenceSetWriteSerializer(serializers.ModelSerializer):

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
        serializers.ModelSerializer):

    class Meta:
        model = DescriptionFormatReferenceSetFull


class ReferenceSetDescriptorReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferenceSetDescriptorReferenceSetDenormalizedView


class ReferenceSetDescriptorPaginationSerializer(
        pagination.PaginationSerializer):

    class Meta:
        object_serializer_class = ReferenceSetDescriptorReadSerializer


class ReferenceSetDescriptorWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferenceSetDescriptorReferenceSetFull
