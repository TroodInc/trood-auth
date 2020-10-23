# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""
import hashlib
import uuid

from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer, ABACResourceSerializer, \
    ABACActionSerializer, ABACAttributeSerializer, ABACPolicySerializer, ABACDomainSerializer, ABACRuleSerializer
from t_auth.api.models import Account, AccountRole, Token, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACDomain, ABACRule
from trood.contrib.django.mail.backends import TroodEmailMessageTemplate



class AccountRoleViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for AccountRole
    """
    queryset = AccountRole.objects.all()
    serializer_class = AccountRoleSerializer
    permission_classes = (IsAuthenticated, )


class AccountViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for Account
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated, )

    def perform_update(self, serializer):
        acc = serializer.save()

        if 'password' in serializer.initial_data:
            Token.objects.filter(account=acc).delete()

    def perform_create(self, serializer):
        password = serializer.initial_data.get('password', get_random_string())

        token = 'acct' + uuid.uuid4().hex
        unique_token = hashlib.sha256(token.encode('utf-8')).hexdigest()

        account = serializer.save(
            unique_token=unique_token,
            pwd_hash=AuthenticationService.get_password_hash(password, unique_token)
        )

        if settings.MAILER_TYPE == 'TROOD':
            message = TroodEmailMessageTemplate(to=[account.login], template='ACCOUNT_REGISTERED', data={
                'username': account.profile['name'],
                'login': account.login,
                'password': password
            })
            message.send()


class ABACResourceViewSet(viewsets.ModelViewSet):
    queryset = ABACResource.objects.all()
    serializer_class = ABACResourceSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("domain", "name", )
    permission_classes = (IsAuthenticated, )


class ABACActionViewSet(viewsets.ModelViewSet):
    queryset = ABACAction.objects.all()
    serializer_class = ABACActionSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource", )
    permission_classes = (IsAuthenticated, )


class ABACAttributViewSet(viewsets.ModelViewSet):
    queryset = ABACAttribute.objects.all()
    serializer_class = ABACAttributeSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource",)
    permission_classes = (IsAuthenticated, )


class ABACDomainViewSet(viewsets.ModelViewSet):
    queryset = ABACDomain.objects.all()
    serializer_class = ABACDomainSerializer
    permission_classes = (IsAuthenticated, )


class ABACPolicyViewSet(viewsets.ModelViewSet):
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer

    # @todo: direct filtering is deprecated, use RQL instead
    
    permission_classes = (IsAuthenticated, )
    filterset_fields = ("resource", "domain", "action", )


class ABACRuleViewSet(viewsets.ModelViewSet):
    """
    Display the ABAC rule.
    """
    queryset = ABACRule.objects.all()
    serializer_class = ABACRuleSerializer
