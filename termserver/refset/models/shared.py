# -coding=utf-8
"""Shared base for all refsets"""
from django.db import models
from django.core.exceptions import ValidationError
from django_extensions.db.fields import PostgreSQLUUIDField

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

    # TODO - add validator to check for presence of correlation_id

    def _validate_correlation(self):
        """Must descend from '447247004 - Map correlation value'"""
        if not SNOMED_TESTER.is_child_of(447247004, self.correlation_id):
            raise ValidationError("The correlation must be a descendant of '447247004'")

    def clean(self):
        """Perform sanity checks"""
        self._validate_correlation()
        super(ComplexExtendedMapReferenceSetBase, self).clean()

    class Meta:
        abstract = True
