# -coding=utf-8
"""Models for core SNOMED components ( refsets excluded )

The initial SNOMED load ( and loading of updates ) will bypass the Django ORM
( for performance reasons, and also to sidestep a "chicken and egg"
 issue with the validators.

This is a PostgreSQL only implementation.
"""
import math
import re

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from djorm_pgarray.fields import BigIntegerArrayField
from djorm_pgarray.fields import TextArrayField
from rest_framework.authtoken.models import Token

from .helpers import verhoeff_digit
from .fields import DenormalizedDescriptionField
from .fields import DenormalizedDescriptionArrayField
from .fields import ExpandedRelationshipField


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


class Component(models.Model):
    """Fields shared between concepts, descriptions and relationships"""
    component_id = models.BigIntegerField()
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()

    # Used by the editing tools to mark the components that have changed
    pending_rebuild = models.NullBooleanField(default=False)

    def _validate_sctid_minimum(self):
        """Must be greater than 10^5"""
        if self.component_id < math.pow(10, 5):
            raise ValidationError("A SNOMED Identifier must be > 10^5")

    def _validate_sctid_maximum(self):
        """Must be less than 10^18"""
        if self.component_id > math.pow(10, 18):
            raise ValidationError("A SNOMED Identifier must be < 10^18")

    def _validate_sctid_is_positive(self):
        """Must be positive integers"""
        if self.component_id < 0:
            raise ValidationError("A SNOMED Identifier must be positive")

    def _validate_sctid_check_digit(self):
        """"The last digit is a Verhoeff dihedral check digit"""
        # Split out last digit
        s = str(self.component_id)
        identifier, check_digit = s[:-1], self._get_sctid_check_digit()
        if verhoeff_digit(identifier) != check_digit:
            raise ValidationError(
                "The SNOMED Identifier has an invalid check digit")

    def _validate_sctid_no_leading_zeros(self):
        """The string rendering of an SCTID should have no leading 0s"""
        pattern = re.compile('^0.+')
        if pattern.match(str(self.component_id)):
            raise ValidationError(
                "The string representation should not have leading zeroes"
            )

    def _sctid_is_short_format(self):
        """True if it contains 00 OR 01 OR 02 as partition identifiers"""
        partition_identifier = self._get_sctid_partition_identifier()
        return partition_identifier in ['00', '01', '02']

    def _sctid_is_long_format(self):
        """True if it contains 10, 11 or 12 as partition identifiers"""
        partition_identifier = self._get_sctid_partition_identifier()
        return partition_identifier in ['10', '11', '12']

    def _get_sctid_check_digit(self):
        """The check digit is always the last digit"""
        return str(self.component_id)[-1]

    def _get_sctid_partition_identifier(self):
        """The partition identifier is always the last two digits"""
        return str(self.component_id)[-3:-1]

    def _validate_identifier_components(self):
        """A valid long format SNOMED identifier has the following components:
            1. Item identifier
            2. Namespace identifier
            3. Partition identifier
            4. Check digit

        A valid short format SNOMED identifier has the following components:
            1. Item identifier
            2. Partition identifier
            3. Check digit
        """
        if (not self._sctid_is_long_format()
                and not self._sctid_is_short_format()):
            raise ValidationError(
                "None of the expected partition identifiers was found")

    def _validate_partition_id(self):
        """Confirm that the partition id corresponds to the component"""
        from core.models import ConceptFull
        from core.models import DescriptionFull
        from core.models import RelationshipFull

        partition_id = self._get_sctid_partition_identifier()
        if isinstance(self, ConceptFull) and partition_id != '10':
            raise ValidationError("Invalid concept partition identifier")
        elif isinstance(self, DescriptionFull) and partition_id != '11':
            raise ValidationError("Invalid description partition identifier")
        elif isinstance(self, RelationshipFull) and partition_id != '12':
            raise ValidationError("Invalid relationship partition identifier")

    def _another_active_component_exists(self):
        """Does another component with the same id exist and is it active?"""
        cls = type(self)
        try:
            return cls.objects.get(
                component_id=self.component_id, active=True).count()
        except cls.DoesNotExist:
            return False

    def _inactivate_older_revisions(self):
        """Inactivate past revisions of this component"""
        cls = type(self)
        for rev in cls.objects.filter(
                component_id=self.component_id, active=True):
            rev.active = False
            rev.save()

    def clean(self):
        """Sanity checks"""
        self._validate_sctid_minimum()
        self._validate_sctid_maximum()
        self._validate_sctid_is_positive()
        self._validate_sctid_is_positive()
        self._validate_sctid_check_digit()
        self._validate_sctid_no_leading_zeros()
        self._validate_identifier_components()
        self._validate_partition_id()
        super(Component, self).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        # We do not allow updates
        if self.pk:
            raise ValidationError(
                "SNOMED Components are immutable; they cannot be altered")

        # Perform sanity checks
        self.full_clean()

        # Next, ensure that only one component can be active at the same time
        # Inactivate older revisions
        if self._another_active_component_exists():
            self._inactivate_older_revisions()

        # Mark for rebuild
        self.pending_rebuild = True

        # Finally, save
        super(Component, self).save(*args, **kwargs)

    def delete(self, using=None):
        """Disable deleting

        :param using:
        """
        raise ValidationError(
            "SNOMED Components are immutable; they cannot be deleted")

    class Meta:
        abstract = True


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


class ConceptDenormalizedView(models.Model):
    """View that pre-computes attributes needed to index/render concepts"""
    id = models.IntegerField(editable=False, primary_key=True)
    concept_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    is_primitive = models.BooleanField(editable=False, default=False)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    definition_status_id = models.BigIntegerField(editable=False)
    definition_status_name = models.TextField(editable=False)

    fully_specified_name = DenormalizedDescriptionField(editable=False)
    preferred_term = DenormalizedDescriptionField(editable=False)
    definition = DenormalizedDescriptionField(
        editable=False, null=True, blank=True)

    descriptions = DenormalizedDescriptionArrayField(editable=False)
    preferred_terms = DenormalizedDescriptionArrayField(editable=False)
    synonyms = DenormalizedDescriptionArrayField(editable=False)

    is_a_parents = ExpandedRelationshipField(editable=False)
    is_a_children = ExpandedRelationshipField(editable=False)
    is_a_direct_parents = ExpandedRelationshipField(editable=False)
    is_a_direct_children = ExpandedRelationshipField(editable=False)

    part_of_parents = ExpandedRelationshipField(editable=False)
    part_of_children = ExpandedRelationshipField(editable=False)
    part_of_direct_parents = ExpandedRelationshipField(editable=False)
    part_of_direct_children = ExpandedRelationshipField(editable=False)

    other_parents = ExpandedRelationshipField(editable=False)
    other_children = ExpandedRelationshipField(editable=False)
    other_direct_parents = ExpandedRelationshipField(editable=False)
    other_direct_children = ExpandedRelationshipField(editable=False)

    @property
    def preferred_term_text(self):
        """A helper for search indexing"""
        return self.preferred_term['term']

    @property
    def fully_specified_name_text(self):
        """A helper for search indexing"""
        return self.fully_specified_name['term']

    @property
    def preferred_terms_list_shortened(self):
        """Extract just the actual preferred terms"""
        return [term['term'] for term in self.preferred_terms] \
            if self.preferred_terms else []

    @property
    def synonyms_list_shortened(self):
        """Extract just the actual synonyms"""
        return [term['term'] for term in self.synonyms] \
            if self.synonyms else []

    @property
    def descriptions_list_shortened(self):
        """Parse the JSON that is embedded inside the descriptions"""
        return [term['term'] for term in self.descriptions] \
            if self.descriptions else []

    @property
    def is_a_parents_ids(self):
        """Extract IDs of is_a_parents"""
        return [rel["concept_id"] for rel in self.is_a_parents] \
            if self.is_a_parents else []

    @property
    def is_a_children_ids(self):
        """Extract IDs of is_a_children"""
        return [rel["concept_id"] for rel in self.is_a_children] \
            if self.is_a_children else []

    class Meta:
        managed = False
        db_table = 'concept_expanded_view'


class DescriptionDenormalizedView(models.Model):
    """Materialized view that pre-computes description attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    language_code = models.CharField(max_length=2, editable=False)
    term = models.TextField(editable=False)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    concept_id = models.BigIntegerField(editable=False)
    concept_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    case_significance_id = models.BigIntegerField(editable=False)
    case_significance_name = models.TextField(editable=False)

    class Meta:
        managed = False
        db_table = 'description_expanded_view'


class RelationshipDenormalizedView(models.Model):
    """Materialized view that pre-computes relationship attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    relationship_group = models.SmallIntegerField(
        editable=False, null=True, blank=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    source_id = models.BigIntegerField(editable=False)
    source_name = models.TextField(editable=False)

    destination_id = models.BigIntegerField(editable=False)
    destination_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    characteristic_type_id = models.BigIntegerField(editable=False)
    characteristic_type_name = models.TextField(editable=False)

    modifier_id = models.BigIntegerField(editable=False)
    modifier_name = models.TextField(editable=False)

    class Meta:
        managed = False
        db_table = 'relationship_expanded_view'


class SubsumptionView(models.Model):
    """Materialized view that pre-computes all subsumption information"""
    concept_id = models.BigIntegerField(editable=False, primary_key=True)

    is_a_direct_parents = BigIntegerArrayField(editable=False)
    is_a_parents = BigIntegerArrayField(editable=False)
    is_a_direct_children = BigIntegerArrayField(editable=False)
    is_a_children = BigIntegerArrayField(editable=False)

    part_of_direct_parents = BigIntegerArrayField(editable=False)
    part_of_parents = BigIntegerArrayField(editable=False)
    part_of_direct_children = BigIntegerArrayField(editable=False)
    part_of_children = BigIntegerArrayField(editable=False)

    other_direct_parents = BigIntegerArrayField(editable=False)
    other_parents = BigIntegerArrayField(editable=False)
    other_direct_children = BigIntegerArrayField(editable=False)
    other_children = BigIntegerArrayField(editable=False)

    class Meta:
        managed = False
        db_table = 'snomed_subsumption'


class SearchContentView(models.Model):
    """Materialized view that pre-computes search index input"""
    id = models.IntegerField(editable=False, primary_key=True)
    concept_id = models.BigIntegerField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    is_primitive = models.BooleanField(editable=False, default=False)
    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)
    fully_specified_name = models.TextField(editable=False)
    preferred_term = models.TextField(editable=False)
    descriptions = TextArrayField(editable=False)
    is_a_parent_ids = BigIntegerArrayField(editable=False)
    is_a_children_ids = BigIntegerArrayField(editable=False)

    class Meta:
        managed = False
        db_table = 'search_content_view'
