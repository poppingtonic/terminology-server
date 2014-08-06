# -*- coding: utf-8 -*-
"""Maintain all refset indexes in one place"""
from __future__ import unicode_literals
from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/14_indexes.sql').read()


class Migration(migrations.Migration):
    """Create indexes"""

    dependencies = [
        ('refset', '0016_auto_20140725_1505'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
