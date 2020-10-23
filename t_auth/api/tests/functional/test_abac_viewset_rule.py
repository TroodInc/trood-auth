import pytest

from rest_framework.test import APITestCase
from t_auth.api.models import ABACDomain, ABACResource, ABACAction, ABACRule, ABACPolicy
from t_auth.api.serializers import ABACPolicyMapSerializer


class ABACViewSetTurnOffRuleTestCase(APITestCase):

    def setUp(self):
        self.domain = ABACDomain.objects.create(pk="TEST_DOMAIN")
        self.resource = ABACResource.objects.create(domain=self.domain, name='RESOURCE', comment='')
        self.action = ABACAction.objects.create(resource=self.resource, name='ACTION')
        self.policy = ABACPolicy.objects.create(active=True, domain=self.domain.pk, action=self.action, resource=self.resource)

    @pytest.mark.django_db
    def test_serealize_only_active_rules(self):
        ABACRule.objects.create(result="allow", rule={}, active=True, policy=self.policy)
        ABACRule.objects.create(result="allow", rule={}, active=False, policy=self.policy)
        policies = ABACPolicy.objects.filter(domain=self.domain.pk, active=True)
        policy_serializer = ABACPolicyMapSerializer(policies)
        active_rule_count = len(policy_serializer.data[self.domain.pk][self.resource.name][self.action.name]) 
        assert active_rule_count == 1

        