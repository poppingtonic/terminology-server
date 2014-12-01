# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('annotation', models.TextField()),
            ],
            options={
                'db_table': 'snomed_annotation_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssociationReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('target_component_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_association_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('value_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_attribute_value_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
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
                ('map_block', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'snomed_complex_map_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('description_format_id', models.BigIntegerField()),
                ('description_length', models.IntegerField()),
            ],
            options={
                'db_table': 'snomed_description_format_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
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
                'db_table': 'snomed_extended_map_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('acceptability_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_language_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('source_effective_time', models.DateField()),
                ('target_effective_time', models.DateField()),
            ],
            options={
                'db_table': 'snomed_module_dependency_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('order', models.PositiveSmallIntegerField()),
                ('linked_to_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_ordered_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('query', models.TextField()),
            ],
            options={
                'db_table': 'snomed_query_specification_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
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
                'db_table': 'snomed_reference_set_descriptor_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
                ('map_target', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'snomed_simple_map_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleReferenceSetFull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_id', django_extensions.db.fields.PostgreSQLUUIDField(auto=False, name=b'row_id')),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('module_id', models.BigIntegerField()),
                ('refset_id', models.BigIntegerField()),
                ('referenced_component_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'snomed_simple_reference_set_full',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnnotationReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'annotation_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnnotationReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'annotation_refset_snapshot',
                'db_table': 'snomed_annotation_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssociationReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'association_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssociationReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'association_refset_snapshot',
                'db_table': 'snomed_association_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'attribute_value_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'attribute_value_refset_snapshot',
                'db_table': 'snomed_attribute_value_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'complex_map_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'complex_map_refset_snapshot',
                'db_table': 'snomed_complex_map_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'description_format_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'description_format_refset_snapshot',
                'db_table': 'snomed_description_format_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'extended_map_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'extended_map_refset_snapshot',
                'db_table': 'snomed_extended_map_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'language_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'language_map_refset_snapshot',
                'db_table': 'snomed_language_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'module_dependency_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'mod_dep_refset_snapshot',
                'db_table': 'snomed_module_dependency_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'ordered_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'ordered_refset_snapshot',
                'db_table': 'snomed_ordered_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'query_specification_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'query_spec_refset_snapshot',
                'db_table': 'snomed_query_specification_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'verbose_name': 'reference set descriptor refset view',
                'db_table': 'reference_set_descriptor_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'refset_descriptor_refset_snapshot',
                'db_table': 'snomed_reference_set_descriptor_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'simple_map_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'simple_map_refset_snapshot',
                'db_table': 'snomed_simple_map_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleReferenceSetDenormalizedView',
            fields=[
            ],
            options={
                'db_table': 'simple_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'simple_refset_snapshot',
                'db_table': 'snomed_simple_reference_set',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
