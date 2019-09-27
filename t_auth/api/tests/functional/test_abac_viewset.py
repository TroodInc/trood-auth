import json

import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from t_auth.api.models import Token, ABACDomain
from t_auth.api.tests.factories import AccountFactory


class ABACViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))


    @pytest.mark.django_db
    def test_create_policy(self):
        ABACDomain.objects.create(pk="TEST")
        response = self.client.post(
            reverse('api:policies-list'),
            data={
                "domain": "TEST",
                "rules": [{
                    "result": "allow",
                    "rule": {"obj.id": 1},
                    "mask": []
                }]
            },
            format='json'
        )
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))

        decoded_response = response.json()
        assert_that(decoded_response['status'], equal_to('OK'))
        assert_that(decoded_response['data']['rules'], has_length(1))
