# -*- coding: utf-8 -*-
"""Enable extensions that will be used to create stored procedures"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/extensions.sql').read()


class Migration(migrations.Migration):
    """Enable Pl/Python and PL/V*"""

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
