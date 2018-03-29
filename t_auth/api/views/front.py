# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import AccountSerializer
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


class TwoFactorViewSet(BaseViewSet):
    """
    Provides external API /check_2fa method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response(self.not_implemented())


class AuthViewSet(BaseViewSet):
    """
    Provides external API /auth method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        token = request.data.get('token')
        if not token:
            data = {
                'error': {
                    'message': 'Not authorized'
                }
            }
            response_code = status.HTTP_401_UNAUTHORIZED
        else:
            account = Account.objects.get(pwd_hash=token)
            data = AccountSerializer(account).data
            response_code = status.HTTP_200_OK
        return Response(self.pack_json(data), status=response_code)
