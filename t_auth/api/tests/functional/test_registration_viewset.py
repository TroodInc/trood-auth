import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.tests.factories import AccountRoleFactory, AccountPermissionFactory


@pytest.mark.django_db
def test_creates_account(client: Client):
    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
    }
    response = client.post(reverse('api:register-list'), data=account_data)
    decoded_response = response.json()
    assert_that(decoded_response['data']['status'], equal_to(OBJECT_STATUS.ACTIVE))
    assert_that(decoded_response['data']['id'], instance_of(int))