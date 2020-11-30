import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from t_auth.api.models import Token, AccountRole, Account
from t_auth.api.tests.factories import AccountFactory
from t_auth.api.domain.services import AuthenticationService


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
        role = AccountRole.objects.create(id="user", name='User', status=AccountRole.STATUS_ACTIVE)
        response = self.client.post(
            reverse('api:account-list'), data={
                'login': 'test@example.com',
                'password': 'testpassword',
                'status': AccountRole.STATUS_ACTIVE,
                'role': role.id
            }
        )

        decoded_response = response.json()
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
        assert_that(decoded_response['status'], equal_to('OK'))
        assert_that(decoded_response['data']['role']['id'], equal_to(role.id))

    @pytest.mark.django_db
    def test_update_account(self):
        response = self.client.patch(
            reverse('api:account-detail', kwargs={'pk': self.account.id}), data={
                'status': AccountRole.STATUS_DISABLED,
            }
        )

        decoded_response = response.json()
        assert_that(decoded_response['data']['status'], is_not(self.account.status))

    @pytest.mark.django_db
    def test_update_another_acccount_password(self):
        account_data = {
            'login': 'test@example.com',
            'password': 'oldpassword',
        }
        response = self.client.post(reverse('register'), data=account_data)

        pwd_hash = AuthenticationService.get_password_hash("admin_pass", "1")
        account = Account.objects.create(login="admin@example.com", pwd_hash=pwd_hash, unique_token="1")
        token = Token.objects.create(account=account)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

        response = self.client.patch(
            reverse('api:account-detail', kwargs={'pk': response.data['id']}),
            data={
                'old_password': 'admin_pass',
                'new_password': 'new_password'
            })
        account = Account.objects.filter(login="test@example.com").first()
        assert account.pwd_hash == AuthenticationService.get_password_hash('new_password', account.unique_token)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_update_acccount_password(self):
        pwd_hash = AuthenticationService.get_password_hash("password", "1")
        account = Account.objects.create(login="admin@test.com", pwd_hash=pwd_hash, unique_token="1")
        token = Token.objects.create(account=account)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))
        response = self.client.patch(
            reverse('api:account-detail', kwargs={'pk': account.id}),
            data={
                'old_password': 'password',
                'new_password': 'new'
            })
        account = Account.objects.filter(id=account.id).first()
        assert account.pwd_hash == AuthenticationService.get_password_hash('new', token.account.unique_token)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_delete_account(self):
        account = AccountFactory()

        response = self.client.delete(
            reverse('api:account-detail', kwargs={'pk': account.id})
        )

        assert_that(response.status_code, equal_to(status.HTTP_204_NO_CONTENT))

    @pytest.mark.django_db
    def test_can_filter_by_rql(self):
        admin_role = AccountRole.objects.create(id="admin", name="Admin")
        client_role = AccountRole.objects.create(id="client", name="Client")

        Account.objects.create(login="admin@test.com", pwd_hash="", unique_token="", role=admin_role)
        Account.objects.create(login="disabled@test.com", pwd_hash="", unique_token="", role=admin_role, active=False)
        Account.objects.create(login="client@test.com", pwd_hash="", unique_token="", role=client_role, )
        Account.objects.create(login="oldclient@test.com", pwd_hash="", unique_token="", role=client_role, active=False)


        response = self.client.get(
            reverse('api:account-list'),
            data={"rql": "eq(active,False)"}
        )

        decoded_response = response.json()
        print(decoded_response)

        assert_that(len(decoded_response['data']), equal_to(2))

        response = self.client.get(
            reverse('api:account-list'),
            data={"rql": "and(eq(active,True),eq(role,admin))"}
        )
        decoded_response = response.json()
        print(decoded_response)

        assert_that(len(decoded_response['data']), equal_to(1))
        assert_that(decoded_response['data'][0]['login'], equal_to('admin@test.com'))
