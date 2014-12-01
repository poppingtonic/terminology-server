# -*- coding: utf-8 -*-
"""Create the dynamic snapshots"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/SQL/0_dynamic_snapshot.sql').read()


class Migration(migrations.Migration):
    """Create the reference set descriptor reference set expanded view"""

    dependencies = [
        ('refset', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
