# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20140930_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='descriptionfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='relationshipfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
    ]
