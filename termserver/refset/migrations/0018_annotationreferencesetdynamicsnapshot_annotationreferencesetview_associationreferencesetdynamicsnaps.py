# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0017_auto_20140806_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'annotation_refset_snapshot',
                'db_table': 'snomed_annotation_reference_set',
                'managed': False,
            },
            bases=('refset.annotationreferenceset',),
        ),
        migrations.CreateModel(
            name='AnnotationReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'annotation_reference_set_expanded_view',
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
            bases=('refset.associationreferenceset',),
        ),
        migrations.CreateModel(
            name='AssociationReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'association_reference_set_expanded_view',
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
            bases=('refset.attributevaluereferenceset',),
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'attribute_value_reference_set_expanded_view',
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
            bases=('refset.complexmapreferenceset',),
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'complex_map_reference_set_expanded_view',
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
            bases=('refset.descriptionformatreferenceset',),
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'description_format_reference_set_expanded_view',
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
            bases=('refset.extendedmapreferenceset',),
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'extended_map_reference_set_expanded_view',
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
            bases=('refset.languagereferenceset',),
        ),
        migrations.CreateModel(
            name='LanguageReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'language_reference_set_expanded_view',
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
            bases=('refset.moduledependencyreferenceset',),
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'module_dependency_reference_set_expanded_view',
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
            bases=('refset.orderedreferenceset',),
        ),
        migrations.CreateModel(
            name='OrderedReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'ordered_reference_set_expanded_view',
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
            bases=('refset.queryspecificationreferenceset',),
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'query_specification_reference_set_expanded_view',
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
            bases=('refset.referencesetdescriptorreferenceset',),
        ),
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSetView',
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
            name='SimpleMapReferenceSetDynamicSnapshot',
            fields=[
            ],
            options={
                'verbose_name': 'simple_map_refset_snapshot',
                'db_table': 'snomed_simple_map_reference_set',
                'managed': False,
            },
            bases=('refset.simplemapreferenceset',),
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'simple_map_reference_set_expanded_view',
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
            bases=('refset.simplereferenceset',),
        ),
        migrations.CreateModel(
            name='SimpleReferenceSetView',
            fields=[
            ],
            options={
                'db_table': 'simple_reference_set_expanded_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
