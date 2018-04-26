# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole, AccountPermission, Token
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import AccountSerializer, AccountPermissionSerializer, LoginResponseSerializer
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
                status__exact=OBJECT_STATUS.ACTIVE,
                login__exact=login
            )

            if AuthenticationService.authenticate(account, password):
                data = LoginResponseSerializer(account).data

                token = Token.objects.create(account=account)

                data['token'] = token.token
                data['expire'] = token.expire.strftime('%Y-%m-%dT%H-%M')
            else:
                data = self.error_json('invalid_credentials')
                raise AuthenticationFailed(data)
        except ObjectDoesNotExist:
            data = self.error_json('invalid_credentials')
            raise AuthenticationFailed(data)
        return Response(self.pack_json(data), status=response_code)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        if 'all' in request.data:
            Token.objects.filter(account_id=request.user.account.id).delete()
        else:
            Token.objects.filter(token=request.user.token.token).delete()

        return Response({}, status=200)


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
        return Response(LoginResponseSerializer(account).data)

# ======================================================================================================================
class TwoFactorViewSet(BaseViewSet):
    """
    Provides external API /check_2fa method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response(self.not_implemented())
