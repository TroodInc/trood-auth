import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from t_auth.api.models import Token, AccountRole
from t_auth.api.tests.factories import AccountFactory


class ABACViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))


    @pytest.mark.django_db
    def test_create_policy(self):
        response = self.client.post(
            reverse('api:policies-list'), data={
                "domain": "CUSTODIAN",
                "rules": [{
                    "result": "allow",
                    "rule": {
                        "and": [
                            {"obj.member.id": "sbj.linked_object.id"},
                            {"sbj.linked_object.role": {"in": [3, 4, 5]}}
                        ]
                    },
                    "mask": ["rating", "member.id"]
                }]
            }
        )

        decoded_response = response.json()
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
        assert_that(decoded_response['status'], equal_to('OK'))
        assert_that(decoded_response['data'], has_key('mask'))
