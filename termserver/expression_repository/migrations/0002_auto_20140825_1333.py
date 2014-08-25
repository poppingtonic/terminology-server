# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expression_repository', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expressionlink',
            name='result_expression_id',
            field=models.ForeignKey(related_name=b'expression_link_result_expression', to='expression_repository.Expression'),
        ),
        migrations.AlterField(
            model_name='expressionlink',
            name='source_expression_id',
            field=models.ForeignKey(related_name=b'expression_link_source_expression', to='expression_repository.Expression'),
        ),
    ]
