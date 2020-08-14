import json

import pytest

from unittest.mock import patch

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from trood.contrib.django.auth.permissions import TroodABACPermission

from t_auth.api.models import Token, ABACDomain, ABACResource, ABACAction
from t_auth.api.tests.factories import AccountFactory, AccountRoleFactory


class ABACViewSetRuleTestCase(APITestCase):

    def setUp(self):
        self.basic_client = APIClient()
        self.admin_client = APIClient()

        self.basic_account = AccountFactory()
        self.basic_role = AccountRoleFactory()
        self.basic_account.role = self.basic_role
        self.basic_account.save()

        self.admin_account = AccountFactory()
        self.admin_role = AccountRoleFactory()
        self.admin_account.role = self.admin_role
        self.admin_account.save()

        token = Token.objects.create(account=self.basic_account)
        self.basic_client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

        token = Token.objects.create(account=self.admin_account)
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    @patch('t_auth.api.views.admin.AccountViewSet.permission_classes', [TroodABACPermission])
    def test_check_policy(self):
        domain = ABACDomain.objects.create(pk="AUTHORIZATION")
        resource = ABACResource.objects.create(domain=domain, name='account', comment='')
        action = ABACAction.objects.create(resource=resource, name='list')
        response = self.admin_client.post(
            reverse('api:policies-list'),
            data={
                "domain": domain.pk,
                "resource": resource.pk,
                "action": action.pk,
                "rules": [
                    {
                        "result": "allow",
                        "rule": {"sbj.role.id": self.admin_role.id},
                        "mask": []
                    },
                    {
                        "result": "deny",
                        "rule": {"sbj.role.id": self.basic_role.id},
                        "mask": []
                    }
                ]
            },
            format='json'
        )
        assert response.status_code == 201

        response = self.basic_client.get(reverse('api:account-list'))
        assert response.status_code == 403

        response = self.admin_client.get(reverse('api:account-list'))
        assert response.status_code == 200
