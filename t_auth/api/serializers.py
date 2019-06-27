# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
import hashlib
import uuid

from django.core.validators import EmailValidator
from rest_framework import serializers, fields, exceptions
from django.utils.translation import ugettext_lazy as _

from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import AccountRole, Account, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACRule


class LoginDataVerificationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name')

    class Meta:
        model = Account
        fields = ('id', 'login', 'created', 'active', 'status', 'role', )


class RegisterSerializer(serializers.Serializer):
    login = fields.EmailField(required=True)
    password = fields.CharField(required=True)

    def validate_login(self, login):
        if Account.objects.filter(login=login).exists():
            raise exceptions.ValidationError('Registered user')
        return login

    def save(self, **kwargs):
        account = AccountFactory.factory(
            login=self.validated_data['login'],
            password=self.validated_data['password']
        )

        return account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = (
            'id', 'login', 'created', 'status', 'active', 'role',
            'pwd_hash', 'type', 'cidr',
        )
        read_only_fields = ('id', 'created', 'pwd_hash',)

    def validate(self, data):
        if data.get('type', None) == Account.SERVICE:
            return super(AccountSerializer, self).validate(data)

        # @todo: validator must be configured in settings
        if 'login' in data:
            validator = EmailValidator(_('Users login must be a valid email address.'))
            validator(data['login'])

        return super(AccountSerializer, self).validate(data)

    def to_internal_value(self, data):
        password = data.get('password', None)
        data = super(AccountSerializer, self).to_internal_value(data)
        if password:
            token = 'acct' + uuid.uuid4().hex
            unique_token = hashlib.sha256(token.encode('utf-8')).hexdigest()

            data.update({
                'unique_token': unique_token,
                'pwd_hash': AuthenticationService.get_password_hash(password, unique_token),
            })

        return data

    def to_representation(self, instance):
        ret = super(AccountSerializer, self).to_representation(instance)
        if instance.type == Account.USER:
            ret.pop('pwd_hash')

        ret['role'] = AccountRoleSerializer(instance.role).data

        return ret


class AccountRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountRole
        fields = ('id', 'name', 'status', )

    def to_representation(self, instance):
        obj = super(AccountRoleSerializer, self).to_representation(instance)

        return obj


class ABACActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABACAction
        fields = ('id', 'name', 'resource', )


class ABACAttributeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="attr_type")

    class Meta:
        model = ABACAttribute
        fields = ('id', 'name', 'type', 'resource', )


class ABACResourceSerializer(serializers.ModelSerializer):
    attributes = ABACAttributeSerializer(many=True, read_only=True)
    actions = ABACActionSerializer(many=True, read_only=True)

    class Meta:
        model = ABACResource
        fields = ('id', 'domain', 'comment', 'name', 'attributes', 'actions')


class ABACRuleSerializer(serializers.ModelSerializer):
    mask = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = ABACRule
        fields = ('result', 'rule', 'mask')


class ABACPolicySerializer(serializers.ModelSerializer):
    rules = ABACRuleSerializer(many=True)

    class Meta:
        model = ABACPolicy
        fields = ('id', 'domain', 'resource', 'action', 'rules')

    def update(self, instance, validated_data):
        rules = validated_data.pop('rules', [])

        policy = super(ABACPolicySerializer, self).update(instance, validated_data)

        if rules:
            policy.rules.all().delete()

        for rule in rules:
            serializer = ABACRuleSerializer(data=rule)
            if serializer.is_valid(raise_exception=True):
                serializer.save(policy=policy)

        return policy

    def create(self, validated_data):
        rules = validated_data.pop('rules', [])
        policy = ABACPolicy.objects.create(**validated_data)

        for rule in rules:
            serializer = ABACRuleSerializer(data=rule)
            if serializer.is_valid(raise_exception=True):
                serializer.save(policy=policy)

        return policy


class ABACPolicyMapSerializer(serializers.Serializer):
    def to_representation(self, data):

        result = {}

        for policy in data:
            if policy.domain not in result:
                result[policy.domain] = {}

            if policy.resource.name not in result[policy.domain]:
                result[policy.domain][policy.resource.name] = {}

            if policy.action.name not in result[policy.domain][policy.resource.name]:
                result[policy.domain][policy.resource.name][policy.action.name] = []

            result[policy.domain][policy.resource.name][policy.action.name] += [
                ABACRuleSerializer(instance=rule).data for rule in policy.rules.all()
            ]

        return result
