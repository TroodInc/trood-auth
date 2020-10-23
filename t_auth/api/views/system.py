import datetime
import json

from django.core import signing
from django.utils import timezone
from django.utils.encoding import force_text
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.conf import settings
from django_redis import get_redis_connection

from t_auth.api.models import Token, ABACResource, ABACAction, ABACAttribute, ABACPolicy, Account
from t_auth.api.serializers import ABACPolicyMapSerializer, LoginDataVerificationSerializer


class VerifyTokenView(APIView):
    """
    Provides external API /auth method
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        token = request.data.get("token", False)

        if request.user.type == Account.USER:
            response = LoginDataVerificationSerializer(request.user).data

            response['profile'] = request.user.profile

            policies = ABACPolicy.objects.filter(active=True)

        if request.user.type == Account.SERVICE:
            token_type = request.data.get("type")
            if token_type == Account.USER:
                try:
                    token_obj = Token.objects.get(token=token)

                    response = LoginDataVerificationSerializer(token_obj.account).data

                    response['profile'] = token_obj.account.profile

                except Token.DoesNotExist:
                    raise exceptions.AuthenticationFailed({"error": "User token invalid"})

                policies = ABACPolicy.objects.filter(active=True)

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

                policies = ABACPolicy.objects.filter(domain=parts[0], active=True)

        response['abac'] = ABACPolicyMapSerializer(policies).data

        if settings.CACHE_TYPE:
            redis = get_redis_connection("default")
            redis.set(f"AUTH:{token}", json.dumps(response), settings.CACHE_TTL)

        return Response(response)


class InvalidateTokenView(APIView):
    """
    Provides service link for cleaning up tokens
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        if 'all' in request.data:
            count, _ = Token.objects.all().delete()
        else:
            now = datetime.datetime.now(tz=timezone.utc)
            count, _ = Token.objects.filter(expire__lt=now).delete()

        return Response({"tokens_removed": count})


class ABACProvisionAttributeMap(APIView):

    permission_classes = (AllowAny, )

    def get(self, request):
        domain = request.GET.get('domain', None)

        if domain:
            policies = ABACPolicy.objects.filter(domain=domain, active=True)
        else:
            policies = ABACPolicy.objects.filter(active=True)

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
