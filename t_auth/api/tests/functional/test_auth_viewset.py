import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.models import Token
from t_auth.api.tests.factories import AccountFactory


class RoleViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

    @pytest.mark.django_db
    def test_returns_account_data_with_valid_token(self):
        account = AccountFactory()
        token = Token.objects.create(account=account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

        response = self.client.post(reverse('verify-token'), )
        decoded_response = response.json()
        assert_that(response.status_code, equal_to(status.HTTP_200_OK))
        assert_that(decoded_response['data']['id'], equal_to(account.id))


    @pytest.mark.django_db
    def test_does_not_return_account_data_with_invalid_token(self):
        response = self.client.post(reverse('verify-token'), )
        decoded_response = response.json()

        assert_that(response.status_code, equal_to(status.HTTP_403_FORBIDDEN))
        assert_that(decoded_response['status'], equal_to('FAIL'))
