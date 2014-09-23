# -*- coding: utf-8 -*-
"""Create the denormalized view that associates concepts with descriptions and relationships"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/10_concept_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the final denormalized concept representation"""

    dependencies = [
        ('core', '0011_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
