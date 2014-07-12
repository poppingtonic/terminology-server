# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='complexmapreferenceset',
            name='map_block_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
