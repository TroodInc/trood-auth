# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer, AccountPermissionSerializer, \
    EndpointSerializer, ABACResourceSerializer, ABACActionSerializer, ABACAttributeSerializer, ABACPolicySerializer
from t_auth.api.models import Account, AccountRole, Token, AccountPermission, Endpoint, ABACResource, ABACAction, \
    ABACAttribute, ABACPolicy


class EndpointsViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for Endpoints
    """
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    permission_classes = (IsAuthenticated,)


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


class PermissionViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD for Permissions
    """
    queryset = AccountPermission.objects.all()
    serializer_class = AccountPermissionSerializer
    permission_classes = (IsAuthenticated, )


class ABACResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ABACResource.objects.all()
    serializer_class = ABACResourceSerializer
    permission_classes = (IsAuthenticated, )


class ABACActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ABACAction.objects.all()
    serializer_class = ABACActionSerializer
    permission_classes = (IsAuthenticated, )


class ABACAttributViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ABACAttribute.objects.all()
    serializer_class = ABACAttributeSerializer
    permission_classes = (IsAuthenticated, )


class ABACPolicyViewSet(viewsets.ModelViewSet):
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer
    permission_classes = (IsAuthenticated,)