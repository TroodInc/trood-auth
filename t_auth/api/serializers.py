# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
import hashlib
import uuid

from rest_framework import serializers

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import AccountPermission, AccountRole, Account, Endpoint


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ('id', 'url', )


class AccountPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountPermission
        fields = ('id', 'endpoint', 'method', 'object_permission')

    def to_representation(self, instance):
        obj = super(AccountPermissionSerializer, self).to_representation(instance)
        obj['endpoint'] = EndpointSerializer(instance.endpoint).data

        return obj


class LoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()

    created = serializers.DateTimeField()
    status = serializers.IntegerField()


class VerificationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name')
    permissions = AccountPermissionSerializer(source='role.permissions', many=True)

    class Meta:
        model = Account
        fields = ('id', 'login', 'created', 'status', 'role', 'permissions')

    def to_representation(self, instance):
        obj = super(VerificationSerializer, self).to_representation(instance)

        if 'permissions' in obj.keys() and obj['permissions']:
            for p in obj['permissions']:
                p['endpoint'] = p['endpoint']['url']

        return obj


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('id', 'login', 'created', 'status', 'role', 'unique_token', 'pwd_hash')
        read_only_fields = ('id', 'created', )

    def to_internal_value(self, data):
        password = data.get('password', None)

        if password:
            token = 'acct' + uuid.uuid4().hex
            unique_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
            new_data = data.copy()
            new_data.update({
                'unique_token': unique_token,
                'pwd_hash': AuthenticationService.get_password_hash(password, unique_token),
            })
            return super(AccountSerializer, self).to_internal_value(new_data)

        return super(AccountSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        ret = super(AccountSerializer, self).to_representation(instance)
        ret.pop('unique_token')
        ret.pop('pwd_hash')
        ret['role'] = AccountRoleSerializer(instance.role).data

        return ret


class AccountRoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=AccountPermission.objects.all())
    class Meta:
        model = AccountRole
        fields = ('id', 'name', 'status', 'permissions')

    def to_representation(self, instance):
        obj = super(AccountRoleSerializer, self).to_representation(instance)
        obj['permissions'] = AccountPermissionSerializer(instance.permissions.all(), many=True).data

        return obj
