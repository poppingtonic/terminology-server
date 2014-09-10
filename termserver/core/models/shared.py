from django.db import models
from django.core.exceptions import ValidationError
from .helpers import verhoeff_digit

import math
import re


class Component(models.Model):
    """Fields shared between all components; ABSTRACT"""
    component_id = models.BigIntegerField()
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()

    def _validate_module_namespace(self):
        """We should only create new content in this server's namespace"""
        pass  # TODO

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
        return str(self.component_id)[-4:-2]

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
        if not self._sctid_is_long_format() and not self._sctid_is_short_format():
            raise ValidationError("None of the expected partition identifiers was found")

    def _validate_partition_id(self):
        """Confirm that the partition id corresponds to the SNOMED identifier"""
        partition_id = self._get_sctid_partition_identifier()
        if isinstance(self, Concept) and partition_id not in ['00', '10']:
            raise ValidationError("Invalid concept partition identifier")
        elif isinstance(self, Description) and partition_id not in ['01', '11']:
            raise ValidationError("Invalid description partition identifier")
        elif isinstance(self, Relationship) and partition_id not in ['02', '12']:
            raise ValidationError("Invalid relationship partition identifier")

    def _validate_module(self):
        """All modules descend from 900000000000443000"""
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.module_id):
            raise ValidationError("The module must be a descendant of '900000000000443000'")

    def _another_active_component_exists(self):
        """Helper; does another component with the same component id exists and is it active?"""
        return self.objects.get(component_id=self.component_id, active=True).count()

    def _inactivate_older_revisions(self):
        """Inactivate past revisions of this component"""
        for rev in self.objects.get(component_id=self.component_id, active=True):
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
        self._validate_module_namespace()
        self._validate_module()
        super(Component, self).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        # We do not allow updates
        if self.pk:
            raise ValidationError("SNOMED Components are immutable; they cannot be altered")

        # Perform sanity checks
        self.full_clean()

        # Next, ensure that only one component can be active at the same time
        # Inactivate older revisions
        if self._another_active_component_exists():
            self._inactivate_older_revisions()

        # Finally, save
        super(Component, self).save(*args, **kwargs)

    def delete(self, using=None):
        """Disable deleting

        :param using:
        """
        raise ValidationError("SNOMED Components are immutable; they cannot be deleted")

    class Meta:
        abstract = True
