import pytest

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.models import Token
from t_auth.api.tests.factories import AccountFactory

from django.core import signing


class RoleViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.account = AccountFactory()
        self.token = Token.objects.create(account=self.account)
        self.service_data = {
            'login': 'TestDomain',
            'type': 'service',
            'status': 'active'
        }

    @pytest.mark.django_db
    def test_returns_account_data_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token.token))

        response = self.client.post(reverse('api:verify-token-list'))
        decoded_response = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert decoded_response['data']['id'] == self.account.id

    @pytest.mark.django_db
    def test_does_not_return_account_data_with_invalid_token(self):
        response = self.client.post(reverse('api:verify-token-list'))
        decoded_response = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert decoded_response['status'] == 'FAIL'

    @pytest.mark.django_db
    def test_returns_service_data_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token.token))
        response = self.client.post(reverse('api:account-list'), data=self.service_data)
        acc = response.json()

        signer = signing.Signer(acc['data']['pwd_hash'], salt="trood.")
        sign = signer.sign(acc['data']['login'])
        self.client.credentials(HTTP_AUTHORIZATION='Service {}'.format(sign))

        response = self.client.post(reverse('api:verify-token-list'))
        decoded_response = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert decoded_response['data']['login'] == acc['data']['login']

    @pytest.mark.django_db
    def test_does_not_return_service_data_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token.token))
        response = self.client.post(reverse('api:account-list'), data=self.service_data)
        acc = response.json()

        self.client.credentials(HTTP_AUTHORIZATION='Service {}:fake_sign'.format(acc['data']['login']))
        response = self.client.post(reverse('api:verify-token-list'))
        decoded_response = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert decoded_response['status'] == 'FAIL'
        assert decoded_response['data']['error'] == 'Incorrect (faked?) token'

    @pytest.mark.django_db
    def test_does_not_return_non_existent_service(self):
        self.client.credentials(HTTP_AUTHORIZATION='Service NotExistentService:fake_sign')

        response = self.client.post(reverse('api:verify-token-list'))
        decoded_response = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert decoded_response['status'] == 'FAIL'
