# -*- coding: utf-8 -*-
"""Create the stored procedure that will pre-compute subsumption relationships"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/1_generate_subsumption_maps.sql').read()


class Migration(migrations.Migration):
    """Pre-compute subsumption relationships"""

    dependencies = [
        ('core', '0002_auto_20140716_1216'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
