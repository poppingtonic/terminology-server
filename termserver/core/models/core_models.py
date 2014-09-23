# -coding=utf-8
"""Models for core SNOMED components ( refsets excluded )

The initial SNOMED load ( and loading of updates ) will bypass the Django ORM
( for performance reasons, and also to sidestep a "chicken and egg"
 issue with the validators.

This is a PostgreSQL only implementation.
"""
from django.db import models
from django.core.exceptions import ValidationError
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

    def _validate_language_code(self):
        if self.language_code != 'en':
            raise ValidationError(
                "The only language permitted in this server is 'en'")

    def _validate_term_length(self):
        if len(self.term) > 32768:
            raise ValidationError("The supplied term is too long")

    def clean(self):
        """Perform sanity checks"""
        self._validate_language_code()
        self._validate_term_length()
        super(self, DescriptionFull).clean()

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

    # TODO - add check that source concept exists
    # TODO - add check that destination concept exists
    # TODO - add check that type exists
    # TODO - add check that characteristic type exists
    # TODO - add check that modifier exists

    def _validate_type(self):
        """Must be set to a descendant of 'Linkage concept [106237007]'"""
        if not SNOMED_TESTER.is_child_of(106237007, self.type.concept_id):
            raise ValidationError("The type must be a descendant of '106237007'")

    def _validate_characteristic_type(self):
        """Must be set to a descendant of '900000000000449001'"""
        if not SNOMED_TESTER.is_child_of(900000000000449001, self.characteristic_type.concept_id):
            raise ValidationError("The characteristic type must be a descendant of '900000000000449001'")

    def _validate_modifier(self):
        """Must be set to a descendant of '900000000000450001'"""
        if not SNOMED_TESTER.is_child_of(900000000000450001, self.modifier.concept_id):
            raise ValidationError("The modifier must be a descendant of '900000000000450001'")

    def clean(self):
        """Sanity checks"""
        self._validate_type()
        self._validate_characteristic_type()
        self._validate_modifier()
        super(self, RelationshipFull).clean()

    class Meta:
        db_table = 'snomed_relationship_full'
