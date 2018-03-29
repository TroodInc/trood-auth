import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory


@pytest.mark.django_db
def test_login_account(client: Client):
    account = AccountFactory()
    account_data = {
        'login': account.login,
        'password': account._password
    }

    response = client.post(reverse('api:login-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['id'], equal_to(account.id))
