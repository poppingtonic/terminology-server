# coding=utf-8
"""Translate between JSON and the terminology server's data model"""
from rest_framework import serializers
from core.models import (ConceptDenormalizedView, DescriptionDenormalizedView,
                         RelationshipDenormalizedView)
from core.models import ConceptFull, DescriptionFull, RelationshipFull


class ConceptReadSerializer(serializers.ModelSerializer):
    # TODO descriptions
    # TODO preferred terms
    # TODO synonyms

    # TODO is_a_parents
    # TODO is_a_children
    # TODO is_a_direct_parents
    # TODO is_a_direct_children

    # TODO part_of_parents
    # TODO part_of_children
    # TODO part_of_direct_parents
    # TODO part_of_direct_children

    # TODO other_parents
    # TODO other_children
    # TODO other_direct_parents
    # TODO other_direct_children

    class Meta:
        model = ConceptDenormalizedView


class DescriptionReadSerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = DescriptionDenormalizedView


class RelationshipReadSerializer(serializers.ModelSerializer):
    pass

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

