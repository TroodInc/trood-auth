import pytest
from hamcrest import *
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.models import Token, AccountRole
from t_auth.api.tests.factories import AccountFactory


class AccountViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    def test_retrieve_accounts_list(self):
        response = self.client.get(reverse('api:account-list'), )
        decoded_response = response.json()

        assert_that(len(decoded_response['data']), equal_to(1))

    @pytest.mark.django_db
    def test_retrieves_account(self):
        response = self.client.get(
            reverse('api:account-detail', kwargs={'pk': self.account.id}),
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['id'], equal_to(self.account.id))

    @pytest.mark.django_db
    def test_create_account(self):
        role = AccountRole.objects.create(name='Test role', status=OBJECT_STATUS.ACTIVE)
        response = self.client.post(
            reverse('api:account-list'), data={
                'login': 'test@example.com',
                'password': 'testpassword',
                'status': OBJECT_STATUS.ACTIVE,
                'role': role.id
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['status'], equal_to('OK'))

    @pytest.mark.django_db
    def test_update_account(self):
        response = self.client.patch(
            reverse('api:account-detail', kwargs={'pk': self.account.id}), data={
                'status': OBJECT_STATUS.DISABLED,
                'password': 'new_password'
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['status'], is_not(self.account.status))

        assert_that(Token.objects.count(), equal_to(0))
