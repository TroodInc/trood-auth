# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.domain.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole, Token
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import LoginResponseSerializer, RegisterSerializer
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

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            account = serializer.save()

            return Response(LoginResponseSerializer(account).data)


class RecoveryView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        login = request.data.get('login', None)

        try:
            account = Account.objects.get(login=login)

            token = Token.objects.create(account=account, type=Token.RECOVERY)

            message_body = render_to_string('recovery.html', context={
                'link': settings.RECOVERY_LINK.format(token.token),
            })

            send_mail(
                _('Password recovery email'),
                message_body,
                from_email=settings.FROM_EMAIL,
                recipient_list=[account.login, ]
            )

            return Response({'detail': 'Recovery link was sent'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'detail': 'Account {} not found'.format(login)}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        token_str = request.data.get('token', None)

        try:
            token = Token.objects.get(token=token_str, type=Token.RECOVERY)

            password = request.data.get('password', None)
            password_confirmation = request.data.get('password_confirmation', None)

            if password == password_confirmation:
                token.account.pwd_hash = AuthenticationService.get_password_hash(password, token.account.unique_token)
                token.account.save()

                token.delete()

                return Response({'detail': 'Password was changed successfuly'}, status=status.HTTP_200_OK)

            else:
                return Response({'detail': "Passwords doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Recovery token {} not found'.format(token_str)},
                status=status.HTTP_404_NOT_FOUND
            )


# ======================================================================================================================
class TwoFactorViewSet(BaseViewSet):
    """
    Provides external API /check_2fa method
    """
    permission_classes = (PublicEndpoint,)

    def create(self, request):
        return Response(self.not_implemented())
