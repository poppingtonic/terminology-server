# coding=utf-8
"""SNOMED expression repository models"""
from django.db import models

from django_extensions.db.fields import PostgreSQLUUIDField
from django.core.exceptions import ValidationError


class Expression(models.Model):
    """Store all unique ( known ) expressions"""
    expression_id = PostgreSQLUUIDField(primary_key=True)
    canonical_expression = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def _validate_expression_length(self):
        if len(self.term) > 900:
            raise ValidationError("The supplied expression is longer than 900 characters")

    def clean(self):
        """Perform sanity checks"""
        self._validate_expression_length()
        super(self, Expression).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        self.full_clean()
        super(Expression, self).save(*args, **kwargs)

    class Meta(object):
        db_table = 'snomed_expression'


class ExpressionLink(models.Model):
    """Store links between a expressions"""
    expression_link_id = PostgreSQLUUIDField(primary_key=True)
    source_expression_id = models.ForeignKey(
        Expression,
        related_name='expression_link_source_expression')
    result_expression_id = models.ForeignKey(
        Expression,
        related_name='expression_link_result_expression'
    )
    transform_type = models.PositiveSmallIntegerField()
    date_in = models.DateTimeField(auto_now_add=True)
    date_out = models.DateTimeField(auto_now_add=True)

    def _validate_transform_type(self):
        """The only valid choices are:
          * 0 -> for the transform from a single concept expression to long normal form
          * 1 -> for the transform from other expression -> long normal form
          * 2 -> for the transform from long normal form to short normal form
        """
        if self.transform_type not in [0,1,2]:
            raise ValidationError("Invalid transform type; only 0, 1 and 2 are allowed")

    def clean(self):
        """Perform sanity checks"""
        self._validate_transform_type()
        super(self, ExpressionLink).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        self.full_clean()
        super(ExpressionLink, self).save(*args, **kwargs)

    class Meta(object):
        db_table = 'snomed_expression_link'
