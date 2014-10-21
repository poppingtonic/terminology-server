from rest_framework import serializers

import json


class DictField(serializers.Field):
    """Read only field to handle DictFields used in denormalized views"""
    def to_native(self, obj):
        try:
            return [json.loads(item) for item in obj]
        except:
            return obj
