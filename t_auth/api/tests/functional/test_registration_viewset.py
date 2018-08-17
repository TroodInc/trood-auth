import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.models import Account
from t_auth.api.tests.factories import AccountRoleFactory


@pytest.mark.django_db
def test_creates_account(client: Client, settings):
    settings.DEFAULT_ACCOUNT_ROLE_ID = None

    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
    }
    response = client.post(reverse('api:register-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['status'], equal_to(Account.STATUS_ACTIVE))
    assert_that(decoded_response['data']['id'], instance_of(int))


@pytest.mark.django_db
def test_creates_account_with_default_role(client: Client, settings):
    account_role = AccountRoleFactory(id="MANAGER")
    settings.DEFAULT_ACCOUNT_ROLE_ID = account_role.id

    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
    }
    response = client.post(reverse('api:register-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['status'], equal_to(Account.STATUS_ACTIVE))
    assert_that(decoded_response['data']['id'], instance_of(int))
    assert_that(decoded_response['data']['role'], equal_to(account_role.id))
