# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0002_complexmapreferenceset_map_block_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='complexmapreferenceset',
            old_name='map_block_id',
            new_name='map_block',
        ),
    ]
