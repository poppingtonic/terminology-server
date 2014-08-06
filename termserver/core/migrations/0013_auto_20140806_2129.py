# -*- coding: utf-8 -*-
"""Create the final denormalized relationship view"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/11_relationship_view.sql').read()


class Migration(migrations.Migration):
    """Create the final denormalized relationship view"""

    dependencies = [
        ('core', '0012_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
