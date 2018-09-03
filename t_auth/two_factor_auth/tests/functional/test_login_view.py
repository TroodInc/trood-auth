import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory
from t_auth.two_factor_auth.domain.constants import MESSAGES, TWO_FACTOR_TYPE, INTERMEDIATE_TOKEN_VERIFICATION_TYPE
from t_auth.two_factor_auth.models import IntermediateToken
from t_auth.two_factor_auth.tests.factories import AuthFactorFactory


@pytest.mark.django_db
def test_login_returns_error_if_2fa_bind_is_not_done(client, settings):
    settings.TWO_FACTOR_AUTH_ENABLED = True
    account = AccountFactory()
    account_data = {
        'login': account.login,
        'password': account._password
    }

    response = client.post(reverse('login'), data=account_data)
    decoded_response = response.json()

    assert_that(response.status_code, equal_to(status.HTTP_403_FORBIDDEN))
    assert_that(decoded_response['data']['error'], equal_to(MESSAGES.TWO_FACTOR_BIND_REQUIRED))


@pytest.mark.django_db
def test_login_returns_message_and_creates_intermediate_token(client, settings):
    settings.TWO_FACTOR_AUTH_ENABLED = True
    account = AccountFactory()
    account_data = {
        'login': account.login,
        'password': account._password
    }
    auth_factor = AuthFactorFactory(account=account, type=TWO_FACTOR_TYPE.SMS)

    response = client.post(reverse('login'), data=account_data)
    decoded_response = response.json()

    assert_that(response.status_code, equal_to(status.HTTP_200_OK))
    assert_that(decoded_response['data']['msg'], equal_to(MESSAGES.TOKEN_HAS_BEEN_SENT))
    assert_that(
        IntermediateToken.objects.filter(
            verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION,
            account=account,
            factor_id=auth_factor.factor_id
        ).count(),
        equal_to(1)
    )
