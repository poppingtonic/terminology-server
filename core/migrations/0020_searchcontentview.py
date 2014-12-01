# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20141028_0828'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchContentView',
            fields=[
            ],
            options={
                'db_table': 'search_content_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
