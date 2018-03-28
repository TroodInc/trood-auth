import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountPermissionFactory, AccountFactory


@pytest.mark.django_db
def test_login_account(client: Client):
    account = AccountFactory()
    permission = AccountPermissionFactory()
    account.permissions.add(permission)

    account_data = {
        'login': account.login,
        'password': account._password
    }

    response = client.post(reverse('api:api_login-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['id'], equal_to(account.id))
    assert_that(decoded_response['data']['permissions'], has_length(1))
    assert_that(decoded_response['data']['permissions'][0]['id'], equal_to(permission.id))


