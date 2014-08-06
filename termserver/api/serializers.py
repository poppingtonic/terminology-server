# coding=utf-8
"""Translate between JSON and the terminology server's data model"""
from rest_framework import serializers

# TODO Use optional, read only and write-only parameters in order to share these between creation and retrieval


class DescriptionSerializer(serializers.Serializer):
    pass


class RelationshipSerializer(serializers.Serializer):
    pass


class ConceptSerializer(serializers.Serializer):
    pass

