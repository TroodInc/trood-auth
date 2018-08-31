import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse

from t_auth.api.tests.factories import AccountFactory
from t_auth.two_factor_auth.domain.constants import EXCEPTIONS


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
    assert_that(decoded_response['data']['error'], equal_to(EXCEPTIONS.TWO_FACTOR_BIND_REQUIRED))
