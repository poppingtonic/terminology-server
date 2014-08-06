# -*- coding: utf-8 -*-
"""Create the final denormalized description view"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/12_description_view.sql').read()


class Migration(migrations.Migration):
    """Create the final denormalized description view"""

    dependencies = [
        ('core', '0013_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
