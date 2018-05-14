from django.utils.deprecation import CallableTrue
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions

from t_auth.api.models import Account, Token


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

        try:
            token = Token.objects.get(token=auth[1], type=Token.AUTHORIZATION)
            user = TroodUser(token.account, token)
            return user, token.token

        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed()


