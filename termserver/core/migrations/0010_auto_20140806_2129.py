# -*- coding: utf-8 -*-
"""Create a stored procedure that extracts the name and id of a concept associated with a relationship"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/8_process_relationships.sql').read()


class Migration(migrations.Migration):
    """Create a stored procedure that helps to link relationships to concepts"""

    dependencies = [
        ('core', '0009_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
