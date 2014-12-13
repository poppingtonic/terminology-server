from rest_framework import serializers

import json
import logging

LOGGER = logging.getLogger(__name__)


class DictField(serializers.Field):
    """Read only field to handle DictFields used in denormalized views"""
    def to_representation(self, obj):
        try:
            l = [json.loads(item) for item in obj]
            LOGGER.debug('Object %s native representation is: %s' % (obj, l))
            return l
        except:
            LOGGER.debug('Unable to load from JSON obj %s' % obj)
            return obj
