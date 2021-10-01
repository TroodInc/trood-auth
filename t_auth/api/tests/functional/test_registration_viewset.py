from unittest.mock import Mock, patch

import pytest
import requests
from django.conf import settings
from django.test import Client
from hamcrest import *
from rest_framework.reverse import reverse

from t_auth.api.models import Account
from t_auth.api.utils import is_captcha_valid


@pytest.mark.django_db
def test_creates_account(client: Client):
    account_data = {
        'login': 'test@example.com',
        'password': 'some-password',
        'сaptcha_key': 'some-key',
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


def test_is_captcha_valid():
    captcha_data = {
        'secret': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
        'response': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    }

    response = requests.post(settings.CAPTCHA_VALIDATION_SERVER, data=captcha_data, verify=True)
    assert response.status_code == 200
    decoded_response = response.json()
    assert_that(decoded_response['success'], equal_to(True))


@patch('t_auth.api.utils.requests.post')
def test_is_mocked_captcha_valid(mock_post):
    mock_post.return_value = Mock(status_code=200, json=lambda: {'success': True})
    response = is_captcha_valid('captcha_key')
    assert_that(response, equal_to(True))
