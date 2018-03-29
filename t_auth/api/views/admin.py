# encoding: utf-8
"""
Auth Service Backend

Administrative endpoints (user and permission lists, actions on users
and permissions)
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import authentication_classes, permission_classes

from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import PermissionSerializer, AccountSerializer
from t_auth.api.models import AccountPermission, Account


class ActionViewSet(viewsets.ViewSet):
    """
    Provides external API /action method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response({'fa': 'action'})


class UserViewSet(viewsets.ViewSet):
    """
    Provides external API /user method
    """
    permission_classes = (PublicEndpoint,)

    def retrieve(self, request, pk=None):
        return Response(AccountSerializer(Account.objects.get(id__exact=pk)).data)


class PermissionViewSet(viewsets.ViewSet):
    """
    Provides external API /permission method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        perm_id = request.GET.get('id', None)

        endpoint = request.data.get('endpoint')
        method = request.data.get('method')
        target_objects = request.data.get('target_objects', False)

        p_object = AccountPermission()

        if perm_id:
            p_object = AccountPermission.objects.get(id__exact=perm_id)

        p_object.endpoint = endpoint
        p_object.method = method
        p_object.target_objects = target_objects

        p_object.save()

        return Response(PermissionSerializer(p_object).data)

    def retrieve(self, request, pk=None):
        p_obj = AccountPermission.objects.get(id__exact=pk)
        return Response(PermissionSerializer(p_obj).data)

    def list(self, request):
        all_permissions = AccountPermission.objects.order_by('endpoint')
        return Response(PermissionSerializer(all_permissions, many=True).data)
