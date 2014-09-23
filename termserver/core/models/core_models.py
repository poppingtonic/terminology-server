# -coding=utf-8
"""Models for core SNOMED components ( refsets excluded )

The initial SNOMED load ( and loading of updates ) will bypass the Django ORM
( for performance reasons, and also to sidestep a "chicken and egg"
 issue with the validators.

This is a PostgreSQL only implementation.
"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .shared import Component


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Ensure that every user has a DRF auth token"""
    if created:
        Token.objects.create(user=instance)


class ServerNamespaceIdentifier(models.Model):
    """Used to account for identifiers issued by this server"""
    extension_item_type = models.CharField(max_length=14, choices=(
        ('DESCRIPTION', 'DESCRIPTION'), ('CONCEPT', 'CONCEPT'),
        ('RELATIONSHIP', 'RELATIONSHIP')
    ))
    extension_item_identifier = models.BigIntegerField()

    class Meta:
        unique_together = ('extension_item_identifier', 'extension_item_type')
        db_table = 'server_namespace_identifier'


class ConceptFull(Component):
    """SNOMED concepts - as loaded from the database"""
    definition_status_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_concept_full'


class DescriptionFull(Component):
    """SNOMED descriptions - as loaded from the database"""
    concept_id = models.BigIntegerField()
    language_code = models.CharField(max_length=2, default='en')
    type_id = models.BigIntegerField()
    case_significance_id = models.BigIntegerField()
    term = models.TextField()

    class Meta:
        db_table = 'snomed_description_full'


class RelationshipFull(Component):
    """SNOMED relationships - as loaded from the database"""
    source_id = models.BigIntegerField()
    destination_id = models.BigIntegerField()
    relationship_group = models.PositiveSmallIntegerField(default=0)
    type_id = models.BigIntegerField()
    characteristic_type_id = models.BigIntegerField()
    modifier_id = models.BigIntegerField()

    class Meta:
        db_table = 'snomed_relationship_full'


class ConceptDynamicSnapshot(Component):
    """Concepts that are current as at the present SNOMED release"""
    definition_status_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_concept'


class DescriptionDynamicSnapshot(Component):
    """Descriptions that are current as at the present SNOMED release"""
    concept_id = models.BigIntegerField()
    language_code = models.CharField(max_length=2, default='en')
    type_id = models.BigIntegerField()
    case_significance_id = models.BigIntegerField()
    term = models.TextField()

    class Meta:
        managed = False
        db_table = 'snomed_description'


class RelationshipDynamicSnapshot(Component):
    """Relationships that are current as at the present SNOMED release"""
    source_id = models.BigIntegerField()
    destination_id = models.BigIntegerField()
    relationship_group = models.PositiveSmallIntegerField(default=0)
    type_id = models.BigIntegerField()
    characteristic_type_id = models.BigIntegerField()
    modifier_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'snomed_relationship'
