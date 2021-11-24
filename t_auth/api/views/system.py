import datetime
import facebook
import json
import requests
import time
import os

from django.core import signing
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.encoding import force_text
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import status

from t_auth.api.models import Token, ABACResource, ABACAction, ABACAttribute, ABACPolicy, Account, ABACRule
from t_auth.api.serializers import ABACPolicyMapSerializer, LoginDataVerificationSerializer


class AccessTokenRegistration(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        access_token = get_authorization_header(request).decode('utf-8').replace('Token ', '')

        response = requests.request(
            url='{}/api/v1.0/o/token/'.format(settings.TROOD_OAUTH_URL.rstrip("/")),
            method='POST',
            headers={'Authorization': f'Token {access_token}'},
            json={"token": access_token, "type": "user"}
        )

        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        data = response.json()['data']
        account, _ = Account.objects.get_or_create(
            login=data['login'], type=Account.USER, active=True
        )

        Token.objects.get_or_create(type=Token.AUTHORIZATION, token=access_token, account=account)

        return Response({"status": "OK"}, status=status.HTTP_200_OK)


class FacebookDataDeletion(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        token = Token.objects.filter(token=request.data.get('token'), type=Token.DELETION).first()

        if token:
            return Response({"detail": "Your data was deleted successfully"})

        return Response({"detail": "Please provide valid deletion token"})

    def post(self, request):
        data = facebook.parse_signed_request(request.data.get('signed_request'), app_secret=settings.FACEBOOK_SECRET)

        # TODO: Remove GDPR marked fields here

        token = Token.objects.create(account=request.user, type=Token.DELETION)

        return Response({
            'url': settings.PROJECT_LINK + '/api/v1.0/facebook-deletion?token=' + token.token,
            'code': token.token
        })


class VerifyTokenViewSet(ViewSet):
    """Provides external API /auth method."""

    permission_classes = (IsAuthenticated,)

    def create(self, request):
        token = request.data.get("token", False)

        policies = ABACPolicy.objects.prefetch_related(
            Prefetch("rules", queryset=ABACRule.objects.filter(active=True)),
            "rules__mask"
        ).select_related("resource", "action").filter(active=True)

        if request.user.type == Account.USER:
            response = LoginDataVerificationSerializer(request.user).data

            response['profile'] = request.user.profile

        if request.user.type == Account.SERVICE:
            token_type = request.data.get("type")
            if token_type == Account.USER:
                try:
                    token_obj = Token.objects.get(token=token)

                    response = LoginDataVerificationSerializer(token_obj.account).data

                    response['profile'] = token_obj.account.profile

                except Token.DoesNotExist:
                    raise exceptions.AuthenticationFailed({"error": "User token invalid"})

            if token_type == Account.SERVICE:

                try:
                    parts = force_text(token).split(':')
                    account = Account.objects.get(login=parts[0])

                    signer = signing.Signer(account.pwd_hash, salt="trood.")

                    try:
                        original = signer.unsign(token)
                        if original != parts[0]:
                            raise exceptions.AuthenticationFailed({"error": "Service token invalid"})

                        response = LoginDataVerificationSerializer(account).data

                    except signing.BadSignature:
                        raise exceptions.AuthenticationFailed({"error": "Incorrect (faked?) token"})

                except Account.DoesNotExist:
                    raise exceptions.AuthenticationFailed({"error": "Service token invalid"})

                policies = policies.filter(domain=parts[0])

        try:
            response['abac'] = ABACPolicyMapSerializer(policies).data
        except UnboundLocalError:
            raise exceptions.AuthenticationFailed({"error": "Incorrect request body. Token and type are missing."})

        if settings.CACHE_TYPE:
            redis = get_redis_connection("default")
            redis.set(f"AUTH:{token}", json.dumps(response), settings.CACHE_TTL)

        return Response(response)


class InvalidateTokenViewSet(ViewSet):
    """
    Provides service link for cleaning up tokens
    """

    def list(self, request):
        if 'all' in request.data:
            count, _ = Token.objects.all().delete()
        else:
            now = datetime.datetime.now(tz=timezone.utc)
            count, _ = Token.objects.filter(expire__lt=now).delete()

        return Response({"tokens_removed": count})


class ABACProvisionAttributeMap(APIView):
    """
    Display the ABAC.
    """
    permission_classes = (AllowAny, )

    def get(self, request):
        domain = request.GET.get('domain', None)

        q = ABACPolicy.objects.prefetch_related(
            Prefetch("rules", queryset=ABACRule.objects.filter(active=True)),
            "rules__mask"
        ).select_related("resource", "action").filter(active=True)

        if domain:
            policies = q.filter(domain=domain)
        else:
            policies = q.all()

        return Response(ABACPolicyMapSerializer(policies).data)

    def post(self, request):
        domain = request.data['domain']

        result = {
            'resources_added': 0,
            'resources_updated': 0,
            'actions_added': 0,
            'actions_updated': 0,
            'attributes_added': 0,
            'attributes_updated': 0,
        }

        def count_results(type, value):
            if value:
                result['{}s_added'.format(type)] += 1
            else:
                result['{}s_updated'.format(type)] += 1

        for resource, options in request.data['resources'].items():
            resource, created = ABACResource.objects.get_or_create(domain=domain, name=resource)
            count_results('resource', created)

            # @todo: need to mark resources/options that not present in tree as removed

            for action in options['actions']:
                action, created = ABACAction.objects.get_or_create(resource=resource, name=action)
                count_results('action', created)

            for attribute in options['attributes']:
                attribute, created = ABACAttribute.objects.get_or_create(resource=resource, name=attribute)
                count_results('attribute', created)

        return Response(result)


class ProbeViewset(ViewSet):
    permission_classes = (AllowAny, )

    def list(self, request):
        return Response(data={
            "status": self.get_status(),
            "version": self.get_version(),
            "uptime": self.get_uptime()
        })

    def get_status(self):
        return "healthy"

    def get_version(self):
        filepath = os.path.join(settings.BASE_DIR, "VERSION")
        with open(filepath, "r") as version_file:
            version = version_file.readlines()
        return "".join(version).strip()

    def get_uptime(self):
        return int(time.time() - settings.START_TIME)
