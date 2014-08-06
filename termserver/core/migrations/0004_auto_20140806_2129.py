# -*- coding: utf-8 -*-
"""Create a materialized view with pre-computed subsumption relationships"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/2_subsumption_view.sql').read()


class Migration(migrations.Migration):
    """Migration to create a materialized view with precomputed subsumption relationships"""

    dependencies = [
        ('core', '0003_auto_20140716_2059'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
