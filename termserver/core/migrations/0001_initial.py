# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

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
                ('definition_status', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
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
                ('language_code', models.CharField(default=b'en', max_length=2)),
                ('term', models.TextField()),
                ('case_significance', models.ForeignKey(to='core.Concept')),
                ('concept', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('type', models.ForeignKey(to='core.Concept')),
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
                ('relationship_group', models.PositiveSmallIntegerField(default=0)),
                ('characteristic_type', models.ForeignKey(to='core.Concept')),
                ('destination', models.ForeignKey(to='core.Concept')),
                ('modifier', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('source', models.ForeignKey(to='core.Concept')),
                ('type', models.ForeignKey(to='core.Concept')),
            ],
            options={
                'db_table': b'snomed_relationship',
            },
            bases=(models.Model,),
        ),
    ]
