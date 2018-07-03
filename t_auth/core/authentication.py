from ipaddress import IPv4Network, IPv4Address

from django.utils.deprecation import CallableTrue
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions

from t_auth.api.models import Token


class TroodUser(object):

    def __init__(self, account, token):
        self.account = account
        self.token = token

    @property
    def is_authenticated(self):
        return CallableTrue


class TroodTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth = get_authorization_header(request).split()

        if not auth or len(auth) != 2:
            return None

        if auth[0] == b'Token':
            try:
                token = Token.objects.get(token=auth[1], type=Token.AUTHORIZATION)

                network = IPv4Network(token.account.cidr)

                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = IPv4Address(x_forwarded_for.split(',')[0])
                else:
                    ip = IPv4Address(request.META.get('REMOTE_ADDR'))

                if ip in network:
                    user = TroodUser(token.account, token)

                    return user, token.token

                raise exceptions.AuthenticationFailed()

            except Token.DoesNotExist:
                raise exceptions.AuthenticationFailed()
