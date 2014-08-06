# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


SQL = open(settings.BASE_DIR + '/core/migrations/SQL/relationship_view.sql').read()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_auto_20140720_0144'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
