from rest_framework import serializers

import json


class JSONField(serializers.Field):
    """Read only field to handle JSONFields used in denormalized views"""
    def to_native(self, obj):
        try:
            return [json.loads(item) for item in obj]
        except:
            return obj
