# -*- coding: utf-8 -*-
"""Create a materialized view that pre-computes descriptions associated with simple map refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/5_simple_map_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the simple map reference set expanded view"""

    dependencies = [
        ('refset', '0007_auto_20140725_1313'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
