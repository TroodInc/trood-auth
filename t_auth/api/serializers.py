# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
from rest_framework import serializers

from t_auth.api.constants import OBJECT_PERMISSION
from t_auth.api.models import AccountPermission
from t_auth.core.utils import ChoicesField


class AccountPermissionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    endpoint = serializers.SlugRelatedField(read_only=True, slug_field='url')
    method = serializers.CharField()
    object_permission = ChoicesField(choices=OBJECT_PERMISSION.CHOICES)

    class Meta:
        model = AccountPermission
        fields = (
            'id',
            'endpoint',
            'method',
            'object_permission'
        )


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()

    created = serializers.DateTimeField()
    status = serializers.IntegerField()
