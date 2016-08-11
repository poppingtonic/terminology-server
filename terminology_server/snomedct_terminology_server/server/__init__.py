from rest_framework import serializers


class BaseDateSerializer(serializers.ModelSerializer):
    effective_time = serializers.DateField(format='iso-8601')
