# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = """
    DROP MATERIALIZED VIEW IF EXISTS relationship_expanded_view CASCADE;
    CREATE MATERIALIZED VIEW relationship_expanded_view AS
    SELECT
      rel.id, rel.effective_time, rel.active, rel.relationship_group,
      rel.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.module_id) AS module_name,
      rel.source_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.source_id) AS source_name,
      rel.destination_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.destination_id) AS destination_name,
      rel.type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.type_id) AS type_name,
      rel.characteristic_type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.characteristic_type_id) AS characteristic_type_name,
      rel.modifier_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.modifier_id) AS modifier_name
    FROM snomed_relationship rel;
    CREATE INDEX snomed_relationship_id ON snomed_relationship(id);
    """

    dependencies = [
        ('core', '0004_auto_20140720_0144'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
