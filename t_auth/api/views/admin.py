# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer, ABACResourceSerializer, \
    ABACActionSerializer, ABACAttributeSerializer, ABACPolicySerializer, ABACDomainSerializer
from t_auth.api.models import Account, AccountRole, Token, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy, ABACDomain


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


class ABACResourceViewSet(viewsets.ModelViewSet):
    queryset = ABACResource.objects.all()
    serializer_class = ABACResourceSerializer
    filter_fields = ("domain", "name", )
    permission_classes = (IsAuthenticated, )


class ABACActionViewSet(viewsets.ModelViewSet):
    queryset = ABACAction.objects.all()
    serializer_class = ABACActionSerializer
    filter_fields = ("resource", )
    permission_classes = (IsAuthenticated, )


class ABACAttributViewSet(viewsets.ModelViewSet):
    queryset = ABACAttribute.objects.all()
    serializer_class = ABACAttributeSerializer
    filter_fields = ("resource",)
    permission_classes = (IsAuthenticated, )


class ABACDomainViewSet(viewsets.ModelViewSet):
    queryset = ABACDomain.objects.all()
    serializer_class = ABACDomainSerializer
    permission_classes = (IsAuthenticated, )


class ABACPolicyViewSet(viewsets.ModelViewSet):
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer
    filter_fields = ("resource", "domain", "action", )
    permission_classes = (IsAuthenticated, )
