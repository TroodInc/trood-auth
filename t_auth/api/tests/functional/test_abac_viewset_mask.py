import json

import pytest

from unittest.mock import patch

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from trood.contrib.django.auth.permissions import TroodABACPermission

from t_auth.api.models import Token, ABACDomain, ABACResource, ABACAction
from t_auth.api.tests.factories import AccountFactory, AccountRoleFactory


class ABACViewSetMaskTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.account = AccountFactory()
        self.role = AccountRoleFactory()
        self.account.role = self.role
        self.account.save()

        token = Token.objects.create(account=self.account)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    @patch('t_auth.api.views.admin.AccountViewSet.permission_classes', [TroodABACPermission])
    def test_check_mask(self):
        domain = ABACDomain.objects.create(pk="AUTHORIZATION")
        resource = ABACResource.objects.create(domain=domain, name='account', comment='')
        action = ABACAction.objects.create(resource=resource, name='list')
        rule = {
            "result": "allow",
            "rule": {},
            "mask": ["language", "profile"]
        }
        data = {
            "domain": domain.pk,
            "resource": resource.pk,
            "action": action.pk,
            "rules": [
                rule
            ]
        }
        response = self.client.post(
            reverse('api:policies-list'),
            data=data,
            format='json'
        )
        assert response.status_code == 201

        rule["mask"] = ["profile"]
        data.update({"rules": [rule]})
        response = self.client.patch(
            reverse('api:policies-detail', kwargs={'pk': self.account.id}),
            data=data,
            format='json'
        )
        assert response.status_code == 200
        assert ["profile"] == response.json()["data"]["rules"][0]["mask"]


