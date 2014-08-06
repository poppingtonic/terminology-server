# -*- coding: utf-8 -*-
"""Create a materialized view that precomputes the descriptions associated with annotation refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/migrations/SQL/annotation_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the annotation reference set expanded view"""

    dependencies = [
        ('refset', '0012_auto_20140725_1446'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
