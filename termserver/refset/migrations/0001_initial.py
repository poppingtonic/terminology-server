# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('annotation', models.TextField()),
            ],
            options={
                'db_table': b'snomed_annotation_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssociationReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('target_component_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_association_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('value_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_attribute_value_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('map_group', models.IntegerField()),
                ('map_priority', models.IntegerField()),
                ('map_rule', models.TextField()),
                ('map_advice', models.TextField()),
                ('map_target', models.CharField(max_length=256)),
                ('correlation_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_complex_map_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('description_format_id', models.BigIntegerField()),
                ('description_length', models.IntegerField()),
            ],
            options={
                'db_table': b'snomed_description_format_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('map_group', models.IntegerField()),
                ('map_priority', models.IntegerField()),
                ('map_rule', models.TextField()),
                ('map_advice', models.TextField()),
                ('map_target', models.CharField(max_length=256)),
                ('correlation_id', models.BigIntegerField()),
                ('map_category_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_extended_map_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('acceptability_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_language_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('source_effective_time', models.DateField()),
                ('target_effective_time', models.DateField()),
            ],
            options={
                'db_table': b'snomed_module_dependency_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('order', models.PositiveSmallIntegerField()),
                ('linked_to_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_ordered_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('query', models.TextField()),
            ],
            options={
                'db_table': b'snomed_query_specification_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('map_target', models.CharField(max_length=256)),
            ],
            options={
                'db_table': b'snomed_simple_map_reference_set',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
            ],
            options={
                'db_table': b'snomed_simple_reference_set',
            },
            bases=(models.Model,),
        ),
    ]
