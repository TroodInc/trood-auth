import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.constants import OBJECT_PERMISSION
from t_auth.api.models import Token
from t_auth.api.tests.factories import AccountFactory, AccountPermissionFactory, EndpointFactory


class EndpointsViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()
        token = Token.objects.create(account=self.account)

        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    @pytest.mark.django_db
    def test_retrieve_endpoints_list(self):
        endpoint = EndpointFactory()

        response = self.client.get(reverse('api:endpoints-list'), )
        decoded_response = response.json()

        assert_that(len(decoded_response['data']), equal_to(1))

    @pytest.mark.django_db
    def test_retrieve_endpoint(self):
        endpoint = EndpointFactory()
        response = self.client.get(
            reverse('api:endpoints-detail', kwargs={'pk': endpoint.id}),
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['id'], equal_to(endpoint.id))

    @pytest.mark.django_db
    def test_create_endpoint(self):
        response = self.client.post(
            reverse('api:endpoints-list'), data={
                'url': '/api/v1.0/test/',
            }
        )
        decoded_response = response.json()
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
        assert_that(decoded_response['status'], equal_to('OK'))

    @pytest.mark.django_db
    def test_update_endpoint(self):
        endpoint = EndpointFactory()
        response = self.client.patch(
            reverse('api:endpoints-detail', kwargs={'pk': endpoint.id}), data={
                'url': '/api/v1.2/test/',
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['url'], is_not(endpoint.url))
