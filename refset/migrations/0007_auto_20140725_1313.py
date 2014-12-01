# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/refset/SQL/4_attribute_value_reference_set_expanded_view.sql').read()


class Migration(migrations.Migration):
    """Create attribute value reference set expanded view"""

    dependencies = [
        ('refset', '0006_auto_20140725_1300'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
