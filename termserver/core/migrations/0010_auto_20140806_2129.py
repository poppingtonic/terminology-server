# -*- coding: utf-8 -*-
"""Procedure that gets the name & id of a concept assoc. with a relationship"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/8_process_relationships.sql').read()


class Migration(migrations.Migration):
    """Create a procedure that helps to link relationships to concepts"""

    dependencies = [
        ('core', '0009_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
