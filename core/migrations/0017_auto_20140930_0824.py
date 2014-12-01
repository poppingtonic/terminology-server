# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20140923_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='conceptfull',
            name='pending_rebuild',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='descriptionfull',
            name='pending_rebuild',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relationshipfull',
            name='pending_rebuild',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
