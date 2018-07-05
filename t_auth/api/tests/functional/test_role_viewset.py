import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.models import Token, AccountRole
from t_auth.api.tests.factories import AccountFactory, AccountRoleFactory


class RoleViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    def test_retrieve_roles_list(self):
        role = AccountRoleFactory()
        role.save()

        response = self.client.get(reverse('api:roles-list'), )
        decoded_response = response.json()

        assert_that(len(decoded_response['data']), equal_to(1))

    @pytest.mark.django_db
    def test_retrieve_role(self):
        role = AccountRoleFactory()
        response = self.client.get(
            reverse('api:roles-detail', kwargs={'pk': role.id}),
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['id'], equal_to(role.id))

    @pytest.mark.django_db
    def test_create_role(self):
        response = self.client.post(
            reverse('api:roles-list'), data={
                'name': 'Test role',
                'status': AccountRole.STATUS_ACTIVE,
            }
        )

        decoded_response = response.json()
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
        assert_that(decoded_response['status'], equal_to('OK'))

    @pytest.mark.django_db
    def test_update_role(self):
        role = AccountRoleFactory()
        response = self.client.patch(
            reverse('api:roles-detail', kwargs={'pk': role.id}), data={
                'status': AccountRole.STATUS_DISABLED,
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['status'], is_not(self.account.status))
