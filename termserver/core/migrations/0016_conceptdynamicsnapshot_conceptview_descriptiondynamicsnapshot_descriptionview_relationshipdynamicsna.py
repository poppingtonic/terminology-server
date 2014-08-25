# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20140806_2129'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptDynamicSnapshot',
            fields=[
            ],
            options={
                'db_table': 'snomed_concept',
                'managed': False,
            },
            bases=('core.concept',),
        ),
        migrations.CreateModel(
            name='ConceptView',
            fields=[
            ],
            options={
                'db_table': 'concept_expanded_view',
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
            bases=('core.concept',),
        ),
        migrations.CreateModel(
            name='DescriptionView',
            fields=[
            ],
            options={
                'db_table': 'description_expanded_view',
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
            bases=('core.concept',),
        ),
        migrations.CreateModel(
            name='RelationshipView',
            fields=[
            ],
            options={
                'db_table': 'relationship_expanded_view',
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
