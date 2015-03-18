# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations


SQL = open(os.path.dirname(__file__) + '/custom.sql').read()


class Migration(migrations.Migration):

    dependencies = [
        ('sil_snomed_core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL)
    ]
