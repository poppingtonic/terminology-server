# -*- coding: utf-8 -*-
"""Materialized view that pre-computes the descriptions that are associated with association refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/association_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the association reference set expanded view"""

    dependencies = [
        ('refset', '0013_auto_20140725_1449'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
