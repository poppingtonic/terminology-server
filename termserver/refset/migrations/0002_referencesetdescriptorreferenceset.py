# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('attribute_description_id', models.BigIntegerField()),
                ('attribute_type_id', models.BigIntegerField()),
                ('attribute_order', models.IntegerField()),
            ],
            options={
                'db_table': b'snomed_reference_set_descriptor_reference_set',
            },
            bases=(models.Model,),
        ),
    ]
