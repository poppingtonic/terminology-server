# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = """
    DROP MATERIALIZED VIEW IF EXISTS attribute_value_reference_set_expanded_view;
    CREATE MATERIALIZED VIEW attribute_value_reference_set_expanded_view AS
    SELECT
      rf.id, rf.row_id, rf.effective_time, rf.active,
      rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
      rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
      rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
      rf.value_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.value_id) AS value_name
    FROM snomed_attribute_value_reference_set rf;
    CREATE INDEX attribute_value_reference_set_expanded_view_id ON attribute_value_reference_set_expanded_view(id);
    CREATE INDEX attribute_value_reference_set_expanded_view_row_id ON attribute_value_reference_set_expanded_view(row_id);
    """

    dependencies = [
        ('refset', '0006_auto_20140725_1300'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
