import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.models import Token
from t_auth.api.tests.factories import AccountFactory


class LoginViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

    @pytest.mark.django_db
    def test_login_account(self):
        account = AccountFactory()
        account_data = {
            'login': account.login,
            'password': account._password
        }

        response = self.client.post(reverse('api:login-list'), data=account_data)
        decoded_response = response.json()

        assert_that(response.status_code, equal_to(status.HTTP_200_OK))
        assert_that(decoded_response['data']['id'], equal_to(account.id))

        token = Token.objects.filter(token=decoded_response['data']['token']).first()

        assert_that(token, not_none())

    @pytest.mark.django_db
    def test_logout_account(self):
        account = AccountFactory()
        token = Token.objects.create(account=account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

        response = self.client.get(reverse('logout'), )

        print(response.content)

        assert_that(response.status_code, equal_to(status.HTTP_200_OK))

        assert_that(len(Token.objects.filter(token=token.token)), equal_to(0))
