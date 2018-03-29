# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""
from rest_framework import viewsets
from rest_framework.response import Response

from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import AccountSerializer
from t_auth.api.models import Account


class ActionViewSet(viewsets.ViewSet):
    """
    Provides external API /action method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response({'fa': 'action'})


class AccountViewSet(viewsets.ViewSet):
    """
    Provides external API /user method
    """
    permission_classes = (PublicEndpoint,)

    def retrieve(self, request, pk=None):
        return Response(AccountSerializer(Account.objects.get(id__exact=pk)).data)


