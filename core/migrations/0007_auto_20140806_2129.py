# -*- coding: utf-8 -*-
"""Create a materialized view that associates concepts and their preferred terms"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/SQL/5_concept_preferred_terms.sql').read()


class Migration(migrations.Migration):
    """Create a view that can be used to rapidly look up a concept's preferred term"""

    dependencies = [
        ('core', '0006_auto_20140806_2129'),
        ('refset', '0002_auto_20140725_1232'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]