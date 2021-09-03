# encoding: utf-8
"""
Auth Service Backend

Object serializers
"""
import hashlib
import uuid

from django.conf import settings
from django.core.validators import EmailValidator
from django.utils.crypto import get_random_string
from rest_framework import serializers, fields, exceptions
from django.utils.translation import ugettext_lazy as _

from trood.contrib.django.serializers import TroodDynamicSerializer

from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import AccountRole, Account, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACRule, ABACDomain

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class AccountRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountRole
        fields = ('id', 'name', 'status', )


class LoginDataVerificationSerializer(serializers.ModelSerializer):
    role = AccountRoleSerializer()

    class Meta:
        model = Account
        fields = ('id', 'login', 'created', 'active', 'status', 'role', 'language', 'type')


class RegisterSerializer(serializers.Serializer):
    login = fields.EmailField(required=True)
    password = fields.CharField(default=get_random_string())
    profile = fields.JSONField(required=False)
    role = fields.IntegerField(required=False)

    def validate_login(self, login):
        if Account.objects.filter(login=login).exists():
            raise exceptions.ValidationError('Registered user')
        return login

    def save(self, **kwargs):
        unique_token = AccountFactory._create_token()
        account = Account.objects.create(
            login=self.validated_data['login'],
            status=Account.STATUS_ACTIVE,
            profile=self.validated_data.get('profile', {}),
            unique_token=unique_token,
            role_id=self.validated_data.get('role'),
            pwd_hash=AuthenticationService.get_password_hash(self.validated_data['password'], unique_token)
        )

        account.owner_id = account.id
        account.save()

        return account


class AccountSerializer(TroodDynamicSerializer):
    profile = fields.JSONField(required=False)
    role = AccountRoleSerializer(required=False, read_only=True)

    class Meta:
        model = Account
        fields = (
            'id', 'login', 'created', 'status', 'active', 'role',
            'pwd_hash', 'type', 'cidr', 'profile', 'language',
        )
        read_only_fields = ('id', 'created', 'pwd_hash',)

    def save(self, **kwargs):
        if 'request' in kwargs:
            instance = super().save(request=kwargs['request'])
        else:
            instance = super().save(**kwargs)
        instance.save()
        return instance

    def validate(self, data):
        if data.get('type', None) == Account.SERVICE:
            return super(AccountSerializer, self).validate(data)

        # @todo: validator must be configured in settings
        if 'login' in data:
            validator = EmailValidator(_('Users login must be a valid email address.'))
            validator(data['login'])

        return super(AccountSerializer, self).validate(data)

    def to_internal_value(self, data):
        role = data.get('role')
        res = super(AccountSerializer, self).to_internal_value(data)
        if role:
            res['role_id'] = role

        return res

    def to_representation(self, instance):
        ret = super(AccountSerializer, self).to_representation(instance)
        if instance.type == Account.USER and 'pwd_hash' in ret:
            ret.pop('pwd_hash')

        return ret


class ABACDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABACDomain
        fields = ('id', 'default_result', )


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
    rule = serializers.JSONField()

    class Meta:
        model = ABACRule
        fields = ('result', 'rule', 'mask', 'active')

    def to_representation(self, instance):
        return {
            'result': instance.result,
            'rule': instance.rule,
            'mask': [m.name for m in instance.mask.all()],
            'active': instance.active
        }


class ABACPolicySerializer(serializers.ModelSerializer):
    rules = ABACRuleSerializer(many=True)

    class Meta:
        model = ABACPolicy
        fields = ('id', 'domain', 'resource', 'action', 'rules', 'active')

    def update(self, instance, validated_data):
        rules = validated_data.pop('rules', [])

        policy = super(ABACPolicySerializer, self).update(instance, validated_data)

        if rules:
            policy.rules.all().delete()

        for rule in rules:
            rule["mask"] = self._set_rule_mask(rule["mask"], validated_data.get('resource'))
            serializer = ABACRuleSerializer(data=rule)
            if serializer.is_valid(raise_exception=True):
                serializer.save(policy=policy)

        return policy

    def create(self, validated_data):
        rules = validated_data.pop('rules', [])
        policy = ABACPolicy.objects.create(**validated_data)

        for rule in rules:
            rule['mask'] = self._set_rule_mask(rule['mask'], validated_data.get('resource'))
            serializer = ABACRuleSerializer(data=rule)
            if serializer.is_valid(raise_exception=True):
                serializer.save(policy=policy)

        return policy

    @staticmethod
    def _set_rule_mask(masks, resource):
        mask = []
        for m in masks:
            obj, created = ABACAttribute.objects.get_or_create(
                name=m, resource=resource
            )
            mask.append(obj.id)
        return mask


class ABACPolicyMapSerializer(serializers.Serializer):
    def to_representation(self, data):

        result = {
            "_default_resolution": settings.ABAC_DEFAULT_RESOLUTION
        }

        for policy in data:
            if policy.domain not in result:
                result[policy.domain] = {

                }

                if policy.resource.domain.default_result is not None:
                    result[policy.domain]["_default_resolution"] = policy.resource.domain.default_result

            if policy.resource.name not in result[policy.domain]:
                result[policy.domain][policy.resource.name] = {}

            if policy.action.name not in result[policy.domain][policy.resource.name]:
                result[policy.domain][policy.resource.name][policy.action.name] = []

            for rule in ABACRuleSerializer(instance=policy.rules, many=True).data:
                result[policy.domain][policy.resource.name][policy.action.name].append(
                    rule
                )

        return result
