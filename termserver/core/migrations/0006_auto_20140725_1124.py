# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/description_view.sql').read()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_auto_20140725_1102'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
