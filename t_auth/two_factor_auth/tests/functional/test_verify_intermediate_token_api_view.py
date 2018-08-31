import pytest
from django.test import Client
from django.urls import reverse
from hamcrest import *
from rest_framework import status

from t_auth.api.tests.factories import AccountFactory
from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE
from t_auth.two_factor_auth.domain.factories import IntermediateTokenFactory
from t_auth.two_factor_auth.domain.services import IntermediateTokenValidationService


@pytest.mark.django_db
def test_creates_second_auth_factor_with_valid_intermediate_token(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.PHONE
    account = AccountFactory()
    factor_id = '79999999999'
    intermediate_token = IntermediateTokenFactory.factory(account=account, factor_id=factor_id,
                                                          factor_type=settings.TWO_FACTOR_AUTH_TYPE)
    data = {
        'factor_id': factor_id,
        'temporary_token': intermediate_token.token,
    }
    response = client.post(reverse('2fa-auth:verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_201_CREATED))
    assert_that(decoded_response['data']['token'], is_not(empty()))
    assert_that(
        IntermediateTokenValidationService.validate(intermediate_token.factor_type, intermediate_token.factor_id,
                                                    intermediate_token.token), is_(None)
    )


@pytest.mark.django_db
def test_returns_error_with_invalid_token_provided(client: Client, settings):
    settings.TWO_FACTOR_AUTH_TYPE = TWO_FACTOR_TYPE.PHONE
    data = {
        'factor_id': '79999999999',
        'temporary_token': 'some-invalid-token',
    }
    response = client.post(reverse('2fa-auth:verify'), data=data)
    decoded_response = response.json()
    assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST))
    assert_that(decoded_response['data']['intermediate_token'][0], equal_to("Provided token is not valid"))
