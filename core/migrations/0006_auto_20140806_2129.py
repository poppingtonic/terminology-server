# -*- coding: utf-8 -*-
"""Create a stored procedure that determines a concept's preferred term"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/4_get_preferred_term.sql').read()


class Migration(migrations.Migration):
    """Create a stored procedure that can be used to extract the preferred term from a list of descriptions"""

    dependencies = [
        ('core', '0005_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
