# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    SQL = """
    CREATE MATERIALIZED VIEW query_specification_reference_set_expanded_view AS
    SELECT
      rf.id, rf.row_id, rf.effective_time, rf.active,
      rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
      rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
      rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
      rf.query
    FROM snomed_query_specification_reference_set rf;
    CREATE INDEX query_specification_reference_set_expanded_view_id ON query_specification_reference_set_expanded_view(id);
    CREATE INDEX query_specification_reference_set_expanded_view_row_id ON query_specification_reference_set_expanded_view(row_id);
    """

    dependencies = [
        ('refset', '0011_auto_20140725_1442'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
