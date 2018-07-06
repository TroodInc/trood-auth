import datetime
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from t_auth.api.models import Token, ABACResource, ABACAction, ABACAttribute, ABACPolicy, Account
from t_auth.api.serializers import ABACPolicyMapSerializer, LoginDataVerificationSerializer


class VerifyTokenView(APIView):
    """
    Provides external API /auth method
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):

        if request.user.type == Account.USER:
            response = LoginDataVerificationSerializer(request.user.account).data
            response['linked_object'] = request.user.account.get_additional_data()

        if request.user.type == Account.SERVICE:
            try:
                token = Token.objects.get(token=request.data.get("token", False))

                response = LoginDataVerificationSerializer(token.account).data

            except Token.DoesNotExist:
                raise exceptions.AuthenticationFailed({"error": "User token invalid"})

        policies = ABACPolicy.objects.all()

        response['abac'] = ABACPolicyMapSerializer(policies).data

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
