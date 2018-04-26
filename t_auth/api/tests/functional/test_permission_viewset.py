import pytest
from hamcrest import *
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.constants import OBJECT_PERMISSION
from t_auth.api.models import Token
from t_auth.api.tests.factories import AccountFactory, AccountPermissionFactory, EndpointFactory


class PermissionViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    def test_retrieve_permissions_list(self):
        permission = AccountPermissionFactory()

        response = self.client.get(reverse('api:permissions-list'), )
        decoded_response = response.json()

        assert_that(len(decoded_response['data']), equal_to(1))

    @pytest.mark.django_db
    def test_retrieve_permission(self):
        permission = AccountPermissionFactory()
        response = self.client.get(
            reverse('api:permissions-detail', kwargs={'pk': permission.id}),
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['id'], equal_to(permission.id))

    @pytest.mark.django_db
    def test_create_permission(self):
        endpoint = EndpointFactory()
        response = self.client.post(
            reverse('api:permissions-list'), data={
                'endpoint': endpoint.id,
                'method': 'POST',
                'object_permission': OBJECT_PERMISSION.ALL_OBJECTS,
            }
        )
        print(response.content)
        decoded_response = response.json()
        assert_that(decoded_response['status'], equal_to('OK'))

    @pytest.mark.django_db
    def test_update_permission(self):
        permission = AccountPermissionFactory()
        response = self.client.patch(
            reverse('api:permissions-detail', kwargs={'pk': permission.id}), data={
                'object_permission': OBJECT_PERMISSION.ALL_OBJECTS,
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['object_permission'], is_not(permission.object_permission))
