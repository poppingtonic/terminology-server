# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Expression',
            fields=[
                ('expression_id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'expression_id')),
                ('canonical_expression', models.TextField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': b'snomed_expression',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExpressionLink',
            fields=[
                ('expression_link_id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'expression_link_id')),
                ('transform_type', models.PositiveSmallIntegerField()),
                ('date_in', models.DateTimeField(auto_now_add=True)),
                ('date_out', models.DateTimeField(auto_now_add=True)),
                ('result_expression_id', models.ForeignKey(to='expression_repository.Expression')),
                ('source_expression_id', models.ForeignKey(to='expression_repository.Expression')),
            ],
            options={
                'db_table': b'snomed_expression_link',
            },
            bases=(models.Model,),
        ),
    ]
