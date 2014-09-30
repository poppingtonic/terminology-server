# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0017_auto_20140806_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='annotationreferencesetdenormalizedview',
            options={'verbose_name': 'annotation_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='associationreferencesetdenormalizedview',
            options={'verbose_name': 'association_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='attributevaluereferencesetdenormalizedview',
            options={'verbose_name': 'attrib_value_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='complexmapreferencesetdenormalizedview',
            options={'verbose_name': 'complex_map_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='descriptionformatreferencesetdenormalizedview',
            options={'verbose_name': 'desc_format_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='descriptionformatreferencesetfull',
            options={'verbose_name': 'description_format_refset_full'},
        ),
        migrations.AlterModelOptions(
            name='extendedmapreferencesetdenormalizedview',
            options={'verbose_name': 'extended_map_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='languagereferencesetdenormalizedview',
            options={'verbose_name': 'lang_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='moduledependencyreferencesetdenormalizedview',
            options={'verbose_name': 'module_dep_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='queryspecificationreferencesetdenormalizedview',
            options={'verbose_name': 'query_spec_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='referencesetdescriptorreferencesetdenormalizedview',
            options={'verbose_name': 'refset_descriptor_refset_view'},
        ),
        migrations.AlterModelOptions(
            name='referencesetdescriptorreferencesetfull',
            options={'verbose_name': 'refset_descriptor_refset_full'},
        ),
        migrations.AlterModelOptions(
            name='simplemapreferencesetdenormalizedview',
            options={'verbose_name': 'simple_map_refset_view'},
        ),
    ]
