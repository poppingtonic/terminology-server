# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-17 06:59
from __future__ import unicode_literals

import os

from django.db import migrations


LOAD_SQL = open(os.path.dirname(__file__) + '/sql/final_load.sql').read()
FULLTEXT_SEARCH_SQL = open(os.path.dirname(__file__) + '/sql/text_search_pipeline.sql').read()

class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(LOAD_SQL),
        migrations.RunSQL(FULLTEXT_SEARCH_SQL)
    ]