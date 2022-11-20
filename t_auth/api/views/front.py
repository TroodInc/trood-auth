# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
from datetime import timedelta

import facebook
import jwt
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.db import DataError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, Token, ABACPolicy
from t_auth.api.permissions import PublicEndpoint
from t_auth.api.serializers import RegisterSerializer, ABACPolicyMapSerializer, LoginDataVerificationSerializer
from t_auth.api.utils import is_captcha_valid, send_registration_mail, send_activation_mail
from trood.contrib.django.mail.backends import TroodEmailMessageTemplate


class AppleAuth(APIView):
    permission_classes = (AllowAny,)

    basename = "apple-auth"

    def make_secret(self):
        headers = {
            'kid': settings.APPLE_KEY_ID
        }

        payload = {
            'iss': settings.APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.APPLE_CLIENT_ID,
        }

        return jwt.encode(
            payload,
            settings.APPLE_PRIVATE_KEY,
            algorithm='ES256',
            headers=headers
        )

    def post(self, request):
        headers = {'content-type': "application/x-www-form-urlencoded"}

        data = {
            'client_id': settings.APPLE_CLIENT_ID,
            'client_secret': self.make_secret(),
            'code': request.data.get('code'),
            'grant_type': 'authorization_code',
        }

        res = requests.post(settings.APPLE_ACCESS_TOKEN_URL, data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get('id_token', None)

        if id_token:
            decoded = jwt.decode(
                id_token, audience=settings.APPLE_CLIENT_ID, algorithms=['RS256'], options={"verify_signature": False}
            )

            account = Account.objects.filter(login=decoded['email']).first()
            if not account:
                account = Account.objects.create(
                    login=decoded['email'], type=Account.USER, active=True,
                    profile_data={
                        "first_name": request.data.get('firstname'),
                        "last_name": request.data.get('lastname')
                    }
                )

            data = make_auth_response(account)
            return Response(data, status=status.HTTP_200_OK)

        raise AuthenticationFailed({"error": "Apple authentication failed"})


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

            data = make_auth_response(account)

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

                data = make_auth_response(account)

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
                captcha_key = request.data.get('captcha_key')

                if captcha_key is None or captcha_key == '' or is_captcha_valid(captcha_key) is False:
                    raise ValidationError({'detail': 'Incorrect captcha_key'})

            if settings.PROFILE_CONFIRMATION_ENABLED:
                account = serializer.save(active=False)

                token = Token.objects.create(account=account, type=Token.ACTIVATION)

                result = LoginDataVerificationSerializer(account).data
                result['profile'] = account.profile

                send_activation_mail({
                    'login': account.login,
                    'password': serializer.data['password'],
                    'project': settings.PROJECT_NAME,
                    'link': settings.PROJECT_LINK,
                    'token': token.token,
                    'profile': account.profile
                })
            else:
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


class ActivateView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        token_str = request.GET.get('token')
        try:
            activation_token = Token.objects.get(token=token_str, type=Token.ACTIVATION)
            activation_token.account.active = True
            activation_token.account.save()

            auth_token = Token.objects.create(account=activation_token.account)

            activation_token.delete()

            return Response({
                'detail': 'Account activated successfully',
                'token': auth_token.token
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Activation token {} not found'.format(token_str)},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        login = request.data.get('login')

        try:
            account = Account.objects.get(login=login)
            token = Token.objects.create(account=account, type=Token.ACTIVATION)

            send_activation_mail({
                'login': account.login,
                'project': settings.PROJECT_NAME,
                'link': settings.PROJECT_LINK,
                'token': token.token,
                'profile': account.profile
            })

            return Response({'detail': 'New activation email was sent'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'User not found'.format(login)},
                status=status.HTTP_404_NOT_FOUND
            )

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
                        'link': settings.RECOVERY_LINK,
                        'token': token.token
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

                return Response({'detail': 'Password was changed successfully'}, status=status.HTTP_200_OK)

            else:
                return Response({'detail': "Passwords doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Recovery token {} not found'.format(token_str)},
                status=status.HTTP_404_NOT_FOUND
            )


def make_auth_response(account):
    data = LoginDataVerificationSerializer(account).data

    token = Token.objects.create(account=account)

    data['token'] = token.token
    data['expire'] = token.expire.strftime('%Y-%m-%dT%H-%M')

    policies = ABACPolicy.objects.filter(active=True)
    data['abac'] = ABACPolicyMapSerializer(policies).data
    data['profile'] = account.profile

    return data
