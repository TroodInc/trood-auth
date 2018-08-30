import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.domain.constants import TOKEN_TYPE
from t_auth.api.models import Token, Account
from t_auth.api.tests.factories import AccountFactory


class PermissionViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory()

    @pytest.mark.djang_db
    def test_recovery_request_was_sent(self):
        response = self.client.post(reverse('password-recovery'), data={'login': self.account.login})

        token = Token.objects.filter(account=self.account, type=TOKEN_TYPE.RECOVERY).first()

        assert_that(response.status_code, equal_to(status.HTTP_200_OK))
        assert_that(token, not_none())

    @pytest.mark.djang_db
    def test_recovery_password_was_changed(self):
        token = Token.objects.create(account=self.account, type=TOKEN_TYPE.RECOVERY)

        old_pwd_hash = self.account.pwd_hash

        new_password = 'test'

        response = self.client.patch(
            reverse('password-recovery'),
            data={'token': token.token, 'password': new_password, 'password_confirmation': new_password}
        )

        updated_account = Account.objects.get(id=self.account.id)

        assert_that(response.status_code, equal_to(status.HTTP_200_OK))
        assert_that(updated_account.pwd_hash, is_not(old_pwd_hash))
