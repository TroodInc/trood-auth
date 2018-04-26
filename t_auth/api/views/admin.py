# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer, AccountPermissionSerializer, \
    EndpointSerializer
from t_auth.api.models import Account, AccountRole, Token, AccountPermission, Endpoint


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


