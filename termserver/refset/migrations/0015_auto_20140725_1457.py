# -*- coding: utf-8 -*-
"""Create a view that precomputes the descriptions associated with module dependency refset attributes"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/refset/SQL/module_dependency_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create the module dependency reference set expanded view"""

    dependencies = [
        ('refset', '0014_auto_20140725_1454'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
