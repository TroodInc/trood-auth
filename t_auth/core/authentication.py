from ipaddress import IPv4Network, IPv4Address

from django.contrib.auth.models import AnonymousUser
from django.core import signing
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.encoding import force_text
from requests import HTTPError
from rest_framework import exceptions, status
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors, url_add_parameters

from trood.contrib.django.auth.engine import TroodABACEngine

from t_auth.api.models import Token, Account, ABACPolicy
from t_auth.api.serializers import ABACPolicyMapSerializer


class TroodOauth2Authentication(BaseOAuth2):
    name = 'trood'
    AUTHORIZATION_URL = '/api/v1.0/o/authorize'
    ACCESS_TOKEN_URL = '/api/v1.0/o/token/'
    REDIRECT_URL = '/authorization/api/v1.0/complete/trood/'

    def start(self):
        access_token = get_authorization_header(self.strategy.request).decode('utf-8').replace('Token ', '')
        self.strategy.session_set('token', access_token)
        if self.uses_redirect():
            return self.strategy.redirect(self.auth_url())
        else:
            return self.strategy.html(self.auth_html())

    def get_redirect_uri(self, state=None):
        """Build redirect with redirect_state parameter."""
        uri = self.strategy.absolute_uri(self.REDIRECT_URL)
        if self.REDIRECT_STATE and state:
            uri = url_add_parameters(uri, {'redirect_state': state})
        return uri

    @staticmethod
    def api_url(path):
        return '{}{}'.format(settings.TROOD_OAUTH_URL.rstrip("/"), path)

    def access_token_url(self):
        return self.api_url(self.ACCESS_TOKEN_URL)

    def authorization_url(self):
        return self.api_url(self.AUTHORIZATION_URL)

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """Completes login process, must return user instance"""
        self.process_error(self.data)

        access_token = self.strategy.session_get('token')
        if access_token is None:
            return JsonResponse({"status": "error", "data": "Token is not valid"}, status=status.HTTP_403_FORBIDDEN)

        data = {}

        try:
            response = self.request(
                self.access_token_url(),
                method='POST',
                headers={'Authorization': f'Token {access_token}'},
                json={"token": access_token, "type": "user"}
            )

            data = response.json()['data']
        except HTTPError as e:
            return JsonResponse(e.response.json(), status=e.response.status_code)

        account, _ = Account.objects.get_or_create(
            login=data['login'], type=Account.USER, active=True
        )

        Token.objects.get_or_create(type=Token.AUTHORIZATION, token=access_token, account=account)

        next = self.strategy.session_get('next')
        if next:
            return redirect(self.strategy.session_get('next'))
        else:
            return JsonResponse({"status": "OK"}, status=status.HTTP_200_OK)


class TroodTokenAuthentication(BaseAuthentication):
    """
    Trood Token Authentication.
    """
    def authenticate(self, request):
        """
        Returns Token and Account.
        """
        auth = get_authorization_header(request).decode("utf-8").split()
        policies = ABACPolicy.objects.filter(domain=settings.SERVICE_DOMAIN)
        policy_serializer = ABACPolicyMapSerializer(policies)
        request.abac = TroodABACEngine(policy_serializer.data)

        if not auth or len(auth) != 2:
            return AnonymousUser(), None
        # checks if the auth is Token or a Service, so returns the account and token.
        if auth[0] == 'Token':
            try:
                token = Token.objects.get(token=auth[1], type=Token.AUTHORIZATION)

                network = IPv4Network(token.account.cidr)

                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = IPv4Address(x_forwarded_for.split(',')[0])
                else:
                    ip = IPv4Address(request.META.get('REMOTE_ADDR'))

                if ip in network:
                    return token.account, token

                raise exceptions.AuthenticationFailed()

            except Token.DoesNotExist:
                raise exceptions.AuthenticationFailed()

        if auth[0] == 'Service':
            try:
                creds = force_text(auth[1]).split(':')
                account = Account.objects.get(login=creds[0])

                signer = signing.Signer(account.pwd_hash, salt="trood.")

                try:
                    original = signer.unsign(auth[1])
                    if original == creds[0]:
                        # TODO: inconsistent with Token case return types(Account and Token instances)
                        return account, Token(token=auth[1], account=account)

                    raise exceptions.AuthenticationFailed()

                except signing.BadSignature:
                    raise exceptions.AuthenticationFailed({"error": "Incorrect (faked?) token"})

            except Token.DoesNotExist:
                raise exceptions.AuthenticationFailed()
