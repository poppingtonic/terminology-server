# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationReferenceSet',
            fields=[
                ('id', django_extensions.db.fields.PostgreSQLUUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('annotation', models.TextField()),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
                ('target_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('target_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('target_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
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
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
                ('value', models.ForeignKey(to='core.Concept')),
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
                ('map_group', models.IntegerField()),
                ('map_priority', models.IntegerField()),
                ('map_rule', models.TextField()),
                ('map_advice', models.TextField()),
                ('map_target', models.CharField(max_length=256)),
                ('correlation', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('description_length', models.IntegerField()),
                ('description_format', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('map_group', models.IntegerField()),
                ('map_priority', models.IntegerField()),
                ('map_rule', models.TextField()),
                ('map_advice', models.TextField()),
                ('map_target', models.CharField(max_length=256)),
                ('correlation', models.ForeignKey(to='core.Concept')),
                ('map_category', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('acceptability', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('source_effective_time', models.DateField()),
                ('target_effective_time', models.DateField()),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('order', models.PositiveSmallIntegerField()),
                ('linked_to', models.ForeignKey(to='core.Concept')),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('query', models.TextField()),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('map_target', models.CharField(max_length=256)),
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
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
                ('module', models.ForeignKey(to='core.Concept')),
                ('referenced_concept', models.ForeignKey(blank=True, to='core.Concept', null=True)),
                ('referenced_description', models.ForeignKey(blank=True, to='core.Description', null=True)),
                ('referenced_relationship', models.ForeignKey(blank=True, to='core.Relationship', null=True)),
                ('refset', models.ForeignKey(to='core.Concept')),
            ],
            options={
                'db_table': b'snomed_simple_reference_set',
            },
            bases=(models.Model,),
        ),
    ]
