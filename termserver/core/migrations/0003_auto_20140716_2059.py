# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/subsumption_view.sql').read()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20140716_1216'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
