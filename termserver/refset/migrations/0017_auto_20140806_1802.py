# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refset', '0016_auto_20140725_1505'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX reference_set_descriptor_reference_set_expanded_view_id ON reference_set_descriptor_reference_set_expanded_view(id);"
            "CREATE INDEX reference_set_descriptor_reference_set_expanded_view_row_id ON reference_set_descriptor_reference_set_expanded_view(row_id);"

            "CREATE INDEX simple_reference_set_expanded_view_id ON simple_reference_set_expanded_view(id);"
            "CREATE INDEX simple_reference_set_expanded_view_row_id ON simple_reference_set_expanded_view(row_id);"

            "CREATE INDEX ordered_reference_set_expanded_view_id ON ordered_reference_set_expanded_view(id);"
            "CREATE INDEX ordered_reference_set_expanded_view_row_id ON ordered_reference_set_expanded_view(row_id);"

            "CREATE INDEX attribute_value_reference_set_expanded_view_id ON attribute_value_reference_set_expanded_view(id);""
            "CREATE INDEX attribute_value_reference_set_expanded_view_row_id ON attribute_value_reference_set_expanded_view(row_id);"

            "CREATE INDEX simple_map_reference_set_expanded_view_id ON simple_map_reference_set_expanded_view(id);""
            "CREATE INDEX simple_map_reference_set_expanded_view_row_id ON simple_map_reference_set_expanded_view(row_id);"

            "CREATE INDEX complex_map_reference_set_expanded_view_id ON complex_map_reference_set_expanded_view(id);"
            "CREATE INDEX complex_map_reference_set_expanded_view_row_id ON complex_map_reference_set_expanded_view(row_id);"

            "CREATE INDEX extended_map_reference_set_expanded_view_id ON extended_map_reference_set_expanded_view(id);"
            "CREATE INDEX extended_map_reference_set_expanded_view_row_id ON extended_map_reference_set_expanded_view(row_id);"

            "CREATE INDEX language_reference_set_expanded_view_id ON language_reference_set_expanded_view(id);"
            "CREATE INDEX language_reference_set_expanded_view_row_id ON language_reference_set_expanded_view(row_id);"

            "CREATE INDEX query_specification_reference_set_expanded_view_id ON query_specification_reference_set_expanded_view(id);"
            "CREATE INDEX query_specification_reference_set_expanded_view_row_id ON query_specification_reference_set_expanded_view(row_id);"

            "CREATE INDEX annotation_reference_set_expanded_view_id ON annotation_reference_set_expanded_view(id);"
            "CREATE INDEX annotation_reference_set_expanded_view_row_id ON annotation_reference_set_expanded_view(row_id);"

            "CREATE INDEX association_reference_set_expanded_view_id ON association_reference_set_expanded_view(id);"
            "CREATE INDEX association_reference_set_expanded_view_row_id ON association_reference_set_expanded_view(row_id);"

            "CREATE INDEX module_dependency_reference_set_expanded_view_id ON module_dependency_reference_set_expanded_view(id);"
            "CREATE INDEX module_dependency_reference_set_expanded_view_row_id ON module_dependency_reference_set_expanded_view(row_id);"

            "CREATE INDEX description_format_reference_set_expanded_view_id ON description_format_reference_set_expanded_view(id);"
            "CREATE INDEX description_format_reference_set_expanded_view_row_id ON description_format_reference_set_expanded_view(row_id);"
        )
    ]
