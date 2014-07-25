# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    SQL = """
    DROP MATERIALIZED VIEW IF EXISTS reference_set_descriptor_reference_set_expanded_view;
    CREATE MATERIALIZED VIEW reference_set_descriptor_reference_set_expanded_view AS
    SELECT
      rf.id, rf.row_id, rf.effective_time, rf.active, rf.attribute_order,
      rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
      rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
      rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
      rf.attribute_description_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.attribute_description_id) AS attribute_description_name,
      rf.attribute_type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.attribute_type_id) AS attribute_type_name
    FROM snomed_reference_set_descriptor_reference_set rf;
    CREATE INDEX reference_set_descriptor_reference_set_expanded_view_id ON reference_set_descriptor_reference_set_expanded_view(id);
    CREATE INDEX reference_set_descriptor_reference_set_expanded_view_row_id ON reference_set_descriptor_reference_set_expanded_view(row_id);
    """

    dependencies = [
        ('refset', '0003_auto_20140712_1827'),
        ('core', '0004_auto_20140720_0144'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
