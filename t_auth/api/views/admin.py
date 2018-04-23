# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import AccountSerializer, AccountRoleSerializer
from t_auth.api.models import Account, AccountRole, Token


class ActionViewSet(viewsets.ViewSet):
    """
    Provides external API /action method
    """
    permission_classes = (PublicEndpoint,)

    def list(self, request):
        return Response(request.user.__dict__)

    def create(self, request):
        return Response({'fa': 'action'})


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



