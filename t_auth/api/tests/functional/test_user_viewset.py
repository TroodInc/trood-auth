import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory, AccountPermissionFactory


@pytest.mark.django_db
def test_retrieves_account(client: Client):
    account = AccountFactory()
    response = client.get(reverse('api:user-detail', kwargs={'pk': account.id}))
    decoded_response = response.json()
    assert_that(decoded_response['data']['id'], equal_to(account.id))


@pytest.mark.django_db
def test_retrieves_account_with_permissions(client: Client):
    account = AccountFactory()
    permission = AccountPermissionFactory()
    account.permissions.add(permission)
    response = client.get(reverse('api:user-detail', kwargs={'pk': account.id}))
    decoded_response = response.json()
    assert_that(decoded_response['data']['permissions'], has_length(1))
    assert_that(decoded_response['data']['permissions'][0]['id'], equal_to(permission.id))
