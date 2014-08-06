# -*- coding: utf-8 -*-
"""Create a materialized view that pre-computes descriptions associated with language refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/8_language_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the language reference set expanded view"""

    dependencies = [
        ('refset', '0010_auto_20140725_1344'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
