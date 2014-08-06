# -*- coding: utf-8 -*-
"""Create a custom PostgreSQL type for descriptions; used by the stored procedures that denormalize concepts"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/3_description_type.sql').read()


class Migration(migrations.Migration):
    """Create a custom PostgreSQL type for descriptions"""

    dependencies = [
        ('core', '0004_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
