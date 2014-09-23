# -*- coding: utf-8 -*-
"""Materialized view that pre-computes the descriptions associated with query specification refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/SQL/9_query_specification_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the query specification refset expanded view"""

    dependencies = [
        ('refset', '0011_auto_20140725_1442'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
