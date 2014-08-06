# -*- coding: utf-8 -*-
"""Materialized view that pre-computes descriptions associated with reference set descriptor refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/1_reference_set_descriptor_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the reference set descriptor reference set expanded view"""

    dependencies = [
        ('refset', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
