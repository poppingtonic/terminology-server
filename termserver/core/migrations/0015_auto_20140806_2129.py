# -*- coding: utf-8 -*-
"""Maintain all indexes in one place"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/13_indexes.sql').read()


class Migration(migrations.Migration):
    """Create indexes for core models and views"""

    dependencies = [
        ('core', '0014_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
