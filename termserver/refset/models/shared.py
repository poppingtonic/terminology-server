# -coding=utf-8
"""Shared base for all refsets"""
from django.db import models
from django_extensions.db.fields import PostgreSQLUUIDField


class RefsetBase(models.Model):
    """Abstract base model for all reference set types"""
    row_id = PostgreSQLUUIDField(auto=False)
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()
    refset_id = models.BigIntegerField()
    referenced_component_id = models.BigIntegerField()

    class Meta:
        abstract = True


class ComplexExtendedMapReferenceSetBase(RefsetBase):
    """Shared base class for both complex and extended reference sets"""
    map_group = models.IntegerField()
    map_priority = models.IntegerField()
    map_rule = models.TextField()
    map_advice = models.TextField()
    map_target = models.CharField(max_length=256)
    correlation_id = models.BigIntegerField()

    class Meta:
        abstract = True
