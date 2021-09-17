# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
import facebook
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.db import DataError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, Token, ABACPolicy
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import RegisterSerializer, ABACPolicyMapSerializer, LoginDataVerificationSerializer
from t_auth.api.utils import is_captcha_valid, send_registration_mail
from trood.contrib.django.mail.backends import TroodEmailMessageTemplate


class FacebookAuth(APIView):
    permission_classes = (AllowAny,)

    basename = "facebook-auth"

    def post(self, request):
        graph = facebook.GraphAPI(access_token=request.data.get("token"), version="2.12")
        fb_user = graph.get_object(id=request.data.get("user"), fields="email")

        if fb_user and "email" in fb_user:
            account, _ = Account.objects.get_or_create(
                login=fb_user['email'], type=Account.USER, active=True
            )

            data = LoginDataVerificationSerializer(account).data

            token = Token.objects.create(account=account)

            data['token'] = token.token
            data['expire'] = token.expire.strftime('%Y-%m-%dT%H-%M')

            policies = ABACPolicy.objects.filter(active=True)
            data['abac'] = ABACPolicyMapSerializer(policies).data
            data['profile'] = account.profile

            return Response(data, status=status.HTTP_200_OK)

        raise AuthenticationFailed({"error": "Facebook user needs to have an email"})


class LoginView(APIView):
    """
    Provides external API /login method
    """
    permission_classes = (PublicEndpoint,)

    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        try:
            account = Account.objects.get(
                login__exact=login
            )

            if AuthenticationService.authenticate(account, password):
                if not account.active:
                    raise AuthenticationFailed({"error": "Account not active"})

                lng = request.data.get("language")
                if lng is not None and lng != account.language:
                    account.language = lng
                    account.save(update_fields=["language"])

                data = LoginDataVerificationSerializer(account).data

                token = Token.objects.create(account=account)

                data['token'] = token.token
                data['expire'] = token.expire.strftime('%Y-%m-%dT%H-%M')

                policies = ABACPolicy.objects.filter(active=True)
                data['abac'] = ABACPolicyMapSerializer(policies).data
                data['profile'] = account.profile

            else:
                raise AuthenticationFailed({"error": f'Invalid password for user {login}'})
        except ObjectDoesNotExist:
            raise AuthenticationFailed({"error": f'User with login {login} not found'})
        except DataError as e:
            raise ValidationError({"error": e})
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        if 'all' in request.data:
            Token.objects.filter(account_id=request.user.id).delete()
        else:
            Token.objects.filter(token=request.auth.token).delete()

        return Response({}, status=200)


class RegistrationViewSet(APIView):
    """
    Provides external API /register method
    """
    permission_classes = (PublicEndpoint,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            if settings.CHECK_CAPTCHA_ENABLED:
                captcha_key = request.data.get('сaptcha_key')

                if not is_captcha_valid(captcha_key):
                    return Response({'detail': "Captcha is not valid"}, status=status.HTTP_400_BAD_REQUEST)

            account = serializer.save()

            result = LoginDataVerificationSerializer(account).data
            token = Token.objects.create(account=account)
            result['token'] = token.token
            result['profile'] = account.profile

            send_registration_mail({
                'login': account.login,
                'password': serializer.data['password'],
                'project': settings.PROJECT_NAME,
                'link': settings.PROJECT_LINK,
                'profile': account.profile
            })

            return Response(result)


class RecoveryView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        login = request.data.get('login', None)

        try:
            account = Account.objects.get(login=login)

            token = Token.objects.create(account=account, type=Token.RECOVERY)

            message_body = render_to_string('recovery.html', context={
                'link': settings.RECOVERY_LINK.format(token.token),
            })

            if settings.MAILER_TYPE == 'TROOD':
                message = TroodEmailMessageTemplate(
                    to=[account.login], template='PASSWORD_RECOVERY', data={
                        'link': settings.RECOVERY_LINK.format(token.token)
                    })
                message.send()
            else:
                message = EmailMessage(
                    to=[account.login],
                    subject=str(_('Password recovery email')),
                    body=message_body
                )
                message.send()

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
