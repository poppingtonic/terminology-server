# -*- coding: utf-8 -*-
"""Create a refset that pre-computes the descriptions associated with extended map refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/7_extended_map_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the extended map reference set expanded view"""

    dependencies = [
        ('refset', '0009_auto_20140725_1338'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
