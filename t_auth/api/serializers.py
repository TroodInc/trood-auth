# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
import hashlib
import uuid

from rest_framework import serializers

from t_auth.api.constants import OBJECT_PERMISSION
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import AccountPermission, AccountRole, Account
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


class LoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()

    created = serializers.DateTimeField()
    status = serializers.IntegerField()


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

        return ret


class AccountRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRole
        fields = ('name', 'status', 'permissions')
