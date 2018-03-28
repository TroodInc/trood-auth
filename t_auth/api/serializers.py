# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    endpoint = serializers.SlugRelatedField(read_only=True, slug_field='url')
    method = serializers.CharField()
    target_objects = serializers.IntegerField()


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    permissions = PermissionSerializer(many=True)

    created = serializers.DateTimeField()
    status = serializers.IntegerField()
