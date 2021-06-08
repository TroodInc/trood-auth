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
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer, ABACResourceSerializer, \
    ABACActionSerializer, ABACAttributeSerializer, ABACPolicySerializer, ABACDomainSerializer, ABACRuleSerializer
from t_auth.api.models import Account, AccountRole, Token, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACDomain, ABACRule
from t_auth.api.utils import send_registration_mail


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
        account = self.get_object()
        old_password = self.request.data.get("old_password")
        new_password = self.request.data.get("new_password")

        if old_password and new_password:
            if self.request.auth:
                if not self.request.auth.account.pwd_hash == AuthenticationService.get_password_hash(old_password, self.request.auth.account.unique_token):
                    raise ValidationError(detail="Incorrect password")
                serializer.save(pwd_hash=AuthenticationService.get_password_hash(new_password, account.unique_token))
                Token.objects.filter(account=account).delete()
        elif not old_password and new_password:
            raise ValidationError(detail="old_password field is required")
        elif not new_password and old_password:
            raise ValidationError(detail="new_password field is required")
        serializer.save(request=self.request)

    def perform_create(self, serializer):
        password = serializer.initial_data.get('password', get_random_string())

        token = 'acct' + uuid.uuid4().hex
        unique_token = hashlib.sha256(token.encode('utf-8')).hexdigest()

        account = serializer.save(
            owner=self.request.user,
            unique_token=unique_token,
            pwd_hash=AuthenticationService.get_password_hash(password, unique_token)
        )

        send_registration_mail({
            'login': account.login,
            'password': password,
            'project': settings.PROJECT_NAME,
            'link': settings.PROJECT_LINK,
            'profile': account.profile
        })


class ABACResourceViewSet(BaseViewSet):
    """
    Display the ABAC resource.
    """
    queryset = ABACResource.objects.all()
    serializer_class = ABACResourceSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("domain", "name", )


class ABACActionViewSet(BaseViewSet):
    """
    Display the ABAC action.
    """
    queryset = ABACAction.objects.all()
    serializer_class = ABACActionSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource", )


class ABACAttributViewSet(BaseViewSet):
    """
    Display the ABAC attribute.
    """
    queryset = ABACAttribute.objects.all()
    serializer_class = ABACAttributeSerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filter_fields = ("resource",)


class ABACDomainViewSet(BaseViewSet):
    """
    Display the ABAC domain.
    """
    queryset = ABACDomain.objects.all()
    serializer_class = ABACDomainSerializer


class ABACPolicyViewSet(BaseViewSet):
    """
    Display the ABAC policy.
    """
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer

    # @todo: direct filtering is deprecated, use RQL instead
    filterset_fields = ("resource", "domain", "action", )


class ABACRuleViewSet(BaseViewSet):
    """
    Display the ABAC rule.
    """
    queryset = ABACRule.objects.all()
    serializer_class = ABACRuleSerializer
