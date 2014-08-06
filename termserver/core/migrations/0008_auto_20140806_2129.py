# -*- coding: utf-8 -*-
"""Create a custom type for description results; used by our stored procedures"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/6_description_result_type.sql').read()


class Migration(migrations.Migration):
    """Create a more lightweight description ( custom PostgreSQL ) type"""

    dependencies = [
        ('core', '0007_auto_20140806_2129'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
