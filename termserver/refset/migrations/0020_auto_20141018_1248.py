# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0019_auto_20140930_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='associationreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='attributevaluereferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='complexmapreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='descriptionformatreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='extendedmapreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='languagereferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='moduledependencyreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='orderedreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='queryspecificationreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='referencesetdescriptorreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='simplemapreferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='simplereferencesetfull',
            name='pending_rebuild',
            field=models.NullBooleanField(default=False),
        ),
    ]
