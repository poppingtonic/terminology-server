# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
from django.conf import settings

SQL = open(settings.BASE_DIR + '/core/migrations/SQL/concept_view.sql', 'r').read()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20140716_2059'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
