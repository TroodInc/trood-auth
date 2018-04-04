import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory


@pytest.mark.django_db
def test_retrieves_account(client: Client):
    account = AccountFactory()
    response = client.get(reverse('api:account-detail', kwargs={'pk': account.id}))
    decoded_response = response.json()
    assert_that(decoded_response['data']['id'], equal_to(account.id))
