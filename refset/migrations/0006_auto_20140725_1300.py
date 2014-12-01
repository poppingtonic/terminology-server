# -*- coding: utf-8 -*-
"""Create a materialized view that pre-computes the descriptions associated with ordered refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/SQL/3_ordered_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create ordered reference set expanded view"""

    dependencies = [
        ('refset', '0005_auto_20140725_1254'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]