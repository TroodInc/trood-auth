# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole, AccountPermission
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import AccountSerializer, AccountPermissionSerializer
from .base import BaseViewSet


class LoginViewSet(BaseViewSet):
    """
    Provides external API /login method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        response_code = status.HTTP_200_OK
        try:
            account = Account.objects.get(
                status__exact=OBJECT_STATUS['active'],
                login__exact=login
            )

            if AuthenticationService.authenticate(account, password):
                data = AccountSerializer(account).data
                data['token'] = account.pwd_hash
            else:
                data = self.error_json('invalid_credentials')
                raise AuthenticationFailed(data)
        except ObjectDoesNotExist:
            data = self.error_json('invalid_credentials')
            raise AuthenticationFailed(data)
        return Response(self.pack_json(data), status=response_code)


class RegistrationViewSet(BaseViewSet):
    """
    Provides external API /register method
    """
    permission_classes = (PublicEndpoint,)

    def get_role(self):
        try:
            return AccountRole.objects.get(id=self.request.data.get('role_id'))
        except AccountRole.DoesNotExist:
            return None

    def create(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        role = self.get_role()
        account = AccountFactory.factory(login=login, password=password, role=role)
        return Response(AccountSerializer(account).data)


class PermissionViewSet(viewsets.ViewSet):
    """
    Provides external API /permission method
    """
    permission_classes = (PublicEndpoint,)

    # def create(self, request):
    #     perm_id = request.GET.get('id', None)
    #
    #     endpoint = request.data.get('endpoint')
    #     method = request.data.get('method')
    #     target_objects = request.data.get('target_objects', False)
    #
    #     p_object = AccountPermission()
    #
    #     if perm_id:
    #         p_object = AccountPermission.objects.get(id__exact=perm_id)
    #
    #     p_object.endpoint = endpoint
    #     p_object.method = method
    #     p_object.target_objects = target_objects
    #
    #     p_object.save()
    #
    #     return Response(PermissionSerializer(p_object).data)

    def list(self, request):
        return Response(AccountPermissionSerializer(AccountPermission.objects.order_by('endpoint'), many=True).data)


class CheckTokenViewSet(BaseViewSet):
    """
    Provides external API /auth method
    """
    permission_classes = (PublicEndpoint,)

    def _get_account(self, token):
        try:
            return Account.objects.get(pwd_hash=token)
        except:
            return None

    def create(self, request):
        token = request.data.get('token')
        if token:
            account = Account.objects.get(pwd_hash=token)
            if account:
                return Response(self.pack_json(AccountSerializer(account).data))
            else:
                raise AuthenticationFailed()
        else:
            raise NotAuthenticated()


class AccountPermissionsViewSet(ModelViewSet):
    serializer_class = AccountPermissionSerializer

    def get_object(self):
        return Account.objects.get(id=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_object().permissions.order_by('endpoint')

    def retrieve(self, request, *args, **kwargs):
        return Response([self.serializer_class(x).data for x in self.get_queryset()])


# ======================================================================================================================
class TwoFactorViewSet(BaseViewSet):
    """
    Provides external API /check_2fa method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response(self.not_implemented())
