# -*- coding: utf-8 -*-
"""Create a view that precomputes descriptions associated with description format reference set entries"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/description_format_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the description format reference set expanded ( materialized ) view"""

    dependencies = [
        ('refset', '0015_auto_20140725_1457'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
