# -*- coding: utf-8 -*-
"""Initial migrations for core SNOMED models"""
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    """Set up models for core SNOMED components"""

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.BigIntegerField()),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('definition_status_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_concept',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.BigIntegerField()),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('concept_id', models.BigIntegerField()),
                ('language_code', models.CharField(default=b'en', max_length=2)),
                ('type_id', models.BigIntegerField()),
                ('case_significance_id', models.BigIntegerField()),
                ('term', models.TextField()),
            ],
            options={
                'db_table': b'snomed_description',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.BigIntegerField()),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('source_id', models.BigIntegerField()),
                ('destination_id', models.BigIntegerField()),
                ('relationship_group', models.PositiveSmallIntegerField(default=0)),
                ('type_id', models.BigIntegerField()),
                ('characteristic_type_id', models.BigIntegerField()),
                ('modifier_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_relationship',
            },
            bases=(models.Model,),
        ),
    ]
