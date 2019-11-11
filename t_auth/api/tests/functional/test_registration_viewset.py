import pytest
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.models import Account


@pytest.mark.django_db
def test_creates_account(client: Client):
    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
    }
    response = client.post(reverse('register'), data=account_data)
    # FIXME: Why 200???
    assert response.status_code == 200
    decoded_response = response.json()
    assert_that(decoded_response['data']['status'], equal_to(Account.STATUS_ACTIVE))
    assert_that(decoded_response['data']['id'], instance_of(int))


@pytest.mark.django_db
def test_not_creates_registared_account(client: Client):
    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
    }
    client.post(reverse('register'), data=account_data)
    
    response = client.post(reverse('register'), data=account_data)
    assert response.status_code == 400
