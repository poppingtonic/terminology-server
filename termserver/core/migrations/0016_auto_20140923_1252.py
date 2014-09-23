# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20140806_2129'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerNamespaceIdentifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extension_item_type', models.CharField(max_length=14, choices=[(b'DESCRIPTION', b'DESCRIPTION'), (b'CONCEPT', b'CONCEPT'), (b'RELATIONSHIP', b'RELATIONSHIP')])),
                ('extension_item_identifier', models.BigIntegerField()),
            ],
            options={
                'db_table': 'server_namespace_identifier',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='servernamespaceidentifier',
            unique_together=set([('extension_item_identifier', 'extension_item_type')]),
        ),
    ]
