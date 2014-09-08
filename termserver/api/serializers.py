# coding=utf-8
"""Translate between JSON and the terminology server's data model"""
from rest_framework import serializers
from core.models import (ConceptDenormalizedView, DescriptionDenormalizedView,
                         RelationshipDenormalizedView)
from core.models import ConceptFull, DescriptionFull, RelationshipFull

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
            'preferred_terms', 'synonyms',
            'is_a_direct_parents', 'is_a_direct_children'
        )


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


class DescriptionReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = DescriptionDenormalizedView


class RelationshipReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationshipDenormalizedView


class ConceptWriteSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = ConceptFull


class DescriptionWriteSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = DescriptionFull


class RelationshipWriteSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = RelationshipFull

