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
    ABACActionSerializer, ABACAttributeSerializer, ABACPolicySerializer, ABACDomainSerializer
from t_auth.api.models import Account, AccountRole, Token, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACDomain
from trood.contrib.django.mail.backends import TroodEmailMessageTemplate


class BaseViewSet(viewsets.ModelViewSet):

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AccountRoleViewSet(BaseViewSet):
    """
    Provides CRUD for AccountRole
    """
    queryset = AccountRole.objects.all()
    serializer_class = AccountRoleSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for Account
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_update(self, serializer):
        acc = serializer.save()

        if 'password' in serializer.initial_data:
            Token.objects.filter(account=acc).delete()

    def perform_create(self, serializer):
        password = serializer.initial_data.get('password', get_random_string())

        token = 'acct' + uuid.uuid4().hex
        unique_token = hashlib.sha256(token.encode('utf-8')).hexdigest()

        account = serializer.save(
            owner=self.request.user,
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


class ABACResourceViewSet(BaseViewSet):
    queryset = ABACResource.objects.all()
    serializer_class = ABACResourceSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("domain", "name", )


class ABACActionViewSet(BaseViewSet):
    queryset = ABACAction.objects.all()
    serializer_class = ABACActionSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource", )


class ABACAttributViewSet(BaseViewSet):
    queryset = ABACAttribute.objects.all()
    serializer_class = ABACAttributeSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource",)


class ABACDomainViewSet(BaseViewSet):
    queryset = ABACDomain.objects.all()
    serializer_class = ABACDomainSerializer


class ABACPolicyViewSet(BaseViewSet):
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource", "domain", "action", )
