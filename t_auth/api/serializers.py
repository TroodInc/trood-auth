# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
from rest_framework import serializers

from t_auth.api.models import AccountPermission


class AccountPermissionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    endpoint = serializers.SlugRelatedField(read_only=True, slug_field='url')
    method = serializers.CharField()
    target_objects = serializers.IntegerField()

    class Meta:
        model = AccountPermission
        fields = (
            'id',
            'endpoint',
            'method',
            'target_objects'
        )


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()

    created = serializers.DateTimeField()
    status = serializers.IntegerField()
