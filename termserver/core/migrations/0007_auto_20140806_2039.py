# -*- coding: utf-8 -*-
"""Create all the core component model / view indexes in the same place"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/indexes.sql').read()


class Migration(migrations.Migration):
    """Create indexes"""

    dependencies = [
        ('core', '0006_auto_20140725_1124'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
