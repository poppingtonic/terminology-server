# -*- coding: utf-8 -*-
"""Create a stored procedure that extracts synonyms, preferred terms, FSN etc from a list of descriptions"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/7_process_descriptions.sql').read()


class Migration(migrations.Migration):
    """Stored procedure that classifies a concept's descriptions"""

    dependencies = [
        ('core', '0008_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
