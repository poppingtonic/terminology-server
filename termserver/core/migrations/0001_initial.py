# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_id', models.BigIntegerField()),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('definition_status_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_concept_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionFull',
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
                'db_table': 'snomed_description_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationshipFull',
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
                'db_table': 'snomed_relationship_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConceptDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'concept_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConceptDynamicSnapshot',
            fields=[
            ],
            options={
                'db_table': 'snomed_concept',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'description_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionDynamicSnapshot',
            fields=[
            ],
            options={
                'db_table': 'snomed_description',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationshipDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'relationship_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationshipDynamicSnapshot',
            fields=[
            ],
            options={
                'db_table': 'snomed_relationship',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubsumptionView',
            fields=[
            ],
            options={
                'db_table': 'snomed_subsumption',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
