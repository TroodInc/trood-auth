from ipaddress import IPv4Network, IPv4Address

from django.contrib.auth.models import AnonymousUser
from django.core import signing
from django.conf import settings
from django.utils.encoding import force_text
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from trood.contrib.django.auth.engine import TroodABACEngine

from t_auth.api.models import Token, Account, ABACPolicy
from t_auth.api.serializers import ABACPolicyMapSerializer


class TroodTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).decode("utf-8").split()
        policies = ABACPolicy.objects.filter(domain=settings.SERVICE_DOMAIN)
        policy_serializer = ABACPolicyMapSerializer(policies)
        request.abac = TroodABACEngine(policy_serializer.data)

        if not auth or len(auth) != 2:
            return AnonymousUser

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
