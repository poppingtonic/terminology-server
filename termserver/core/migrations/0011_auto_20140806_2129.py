# -*- coding: utf-8 -*-
"""Create a materialized view that joins concepts to descriptions and the language reference set(s)"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/9_con_desc_cte.sql').read()


class Migration(migrations.Migration):
    """Create the first view that joins concepts to descriptions and language reference set entries"""

    dependencies = [
        ('core', '0010_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
