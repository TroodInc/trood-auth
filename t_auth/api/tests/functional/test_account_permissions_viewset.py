import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory, AccountPermissionFactory


@pytest.mark.django_db
def test_returns_account_permissions(client: Client):
    account = AccountFactory()
    another_account = AccountFactory()

    permission1 = AccountPermissionFactory()
    permission2 = AccountPermissionFactory()

    account.permissions.add(permission1)
    account.permissions.add(permission2)

    another_account.permissions.add(permission1)

    response = client.get(reverse('api:account-permissions-detail', kwargs={'pk': account.id}))
    decoded_response = response.json()
    print (response.content)
    assert_that(decoded_response['status'], equal_to('OK'))
    assert_that(decoded_response['data'], has_length(2))
    assert_that(decoded_response['data'][0]['id'], equal_to(permission1.id))
    assert_that(decoded_response['data'][1]['id'], equal_to(permission2.id))
