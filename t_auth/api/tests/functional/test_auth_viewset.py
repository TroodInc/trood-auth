import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory


@pytest.mark.django_db
def test_returns_account_data_with_valid_token(client: Client):
    account = AccountFactory()
    account_data = {
        'token': account.pwd_hash
    }
    response = client.post(reverse('api:api_auth-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['id'], equal_to(account.id))


@pytest.mark.django_db
def test_does_not_return_account_data_with_invalid_token(client: Client):
    account_data = {
        'token': 'wrong_token'
    }
    response = client.post(reverse('api:api_auth-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['status'], equal_to('FAIL'))
