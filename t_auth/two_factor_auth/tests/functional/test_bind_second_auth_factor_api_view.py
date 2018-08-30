import pytest
from django.test import Client
from django.urls import reverse
from hamcrest import *
from rest_framework import status

from t_auth.api.tests.factories import AccountFactory
from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE
from t_auth.two_factor_auth.models import IntermediateToken
from t_auth.two_factor_auth.tests.factories import SecondAuthFactorFactory


@pytest.mark.django_db
def test_creates_and_returns_intermediate_token_on(client: Client):
    account = AccountFactory()
    data = {
        'login': account.login,
        'factor_id': '79999999999'
    }

    response = client.post(reverse('2fa-auth:bind'), data=data)
    decoded_response = response.json()

    assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
    assert_that(decoded_response['data']['temporary_token'], has_length(6))
    assert_that(IntermediateToken.objects.get(token=decoded_response['data']['temporary_token']),
                instance_of(IntermediateToken))


@pytest.mark.django_db
def test_returns_error_with_invalid_phone_number(client: Client):
    account = AccountFactory()
    data = {
        'login': account.login,
        'factor_id': '79999999'
    }

    response = client.post(reverse('2fa-auth:bind'), data=data)
    decoded_response = response.json()

    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['factor_id'][0], equal_to('Phone has invalid length'))


@pytest.mark.django_db
def test_returns_error_with_duplicated_phone_number(client: Client):
    account = AccountFactory()
    phone_number = '79999999999'
    SecondAuthFactorFactory(account=account, factor_id=phone_number, type=TWO_FACTOR_TYPE.PHONE)
    data = {
        'login': account.login,
        'factor_id': phone_number
    }

    response = client.post(reverse('2fa-auth:bind'), data=data)
    decoded_response = response.json()

    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['factor_id'][0], equal_to('Account with that phone already exists'))
