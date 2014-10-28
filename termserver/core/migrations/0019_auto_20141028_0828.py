# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


SQL = open(settings.BASE_DIR + '/core/SQL/13_search_content_view.sql').read()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20141018_1248'),
    ]
    operations = [
        migrations.RunSQL(SQL),
    ]
