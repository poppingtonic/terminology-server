# -*- coding: utf-8 -*-
"""Create a materialized view that pre-computes the descriptions associated with simple refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/simple_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the simple reference set expanded view"""

    dependencies = [
        ('refset', '0004_auto_20140725_1233'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
