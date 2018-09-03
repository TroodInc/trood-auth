import datetime

import pytest
from django.test import Client
from django.urls import reverse
from hamcrest import *
from rest_framework import status

from t_auth.api.tests.factories import AccountFactory
from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE, INTERMEDIATE_TOKEN_VERIFICATION_TYPE, MESSAGES
from t_auth.two_factor_auth.domain.factories import IntermediateTokenFactory
from t_auth.two_factor_auth.domain.services import IntermediateTokenValidationService
from t_auth.two_factor_auth.tests.factories import AuthFactorFactory


@pytest.mark.django_db
def test_logins_with_valid_intermediate_token(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.SMS
    account = AccountFactory()
    auth_factor = AuthFactorFactory(account=account)
    intermediate_token = IntermediateTokenFactory.factory(
        account=account,
        factor_id=auth_factor.id,
        factor_type=settings.TWO_FACTOR_AUTH_TYPE,
        verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
    )
    data = {
        'factor_id': auth_factor.id,
        'temporary_token': intermediate_token.token,
    }
    response = client.post(reverse('2fa-auth:auth-verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
    assert_that(decoded_response['data']['token'], is_not(empty()))
    assert_that(
        IntermediateTokenValidationService.validate(
            intermediate_token.factor_type,
            intermediate_token.factor_id,
            intermediate_token.token,
            INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
        ), is_(None)
    )


@pytest.mark.django_db
def test_returns_error_with_invalid_token_provided(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.SMS
    data = {
        'factor_id': '79999999999',
        'temporary_token': 'some-invalid-token',
    }
    response = client.post(reverse('2fa-auth:auth-verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['intermediate_token'][0], equal_to(MESSAGES.TOKEN_IS_INVALID))


@pytest.mark.django_db
def test_returns_error_with_expired_token_provided(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.SMS
    account = AccountFactory()
    auth_factor = AuthFactorFactory(account=account)

    #
    intermediate_token = IntermediateTokenFactory.factory(
        account=account,
        factor_id=auth_factor.id,
        factor_type=settings.TWO_FACTOR_AUTH_TYPE,
        verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
    )
    # set expired datetime
    intermediate_token.expire = intermediate_token.expire - datetime.timedelta(
        minutes=settings.TWO_FACTOR_INTERMEDIATE_TOKEN_TTL + 1
    )
    intermediate_token.save()

    data = {
        'factor_id': auth_factor.id,
        'temporary_token': intermediate_token.token,
    }
    response = client.post(reverse('2fa-auth:auth-verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['intermediate_token'][0], equal_to(MESSAGES.TOKEN_IS_INVALID))


@pytest.mark.django_db
def test_returns_error_with_used_token_provided(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.SMS
    account = AccountFactory()
    auth_factor = AuthFactorFactory(account=account)

    #
    intermediate_token = IntermediateTokenFactory.factory(
        account=account,
        factor_id=auth_factor.id,
        factor_type=settings.TWO_FACTOR_AUTH_TYPE,
        verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
    )
    # set token as used
    intermediate_token.used = True
    intermediate_token.save()

    data = {
        'factor_id': auth_factor.id,
        'temporary_token': intermediate_token.token,
    }
    response = client.post(reverse('2fa-auth:auth-verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['intermediate_token'][0], equal_to(MESSAGES.TOKEN_IS_INVALID))
