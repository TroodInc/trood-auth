import pytest
from hamcrest import *
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from t_auth.api.models import Token, Account
from t_auth.api.tests.factories import AccountFactory


class UserActivationViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.account = AccountFactory(active=False)

    @pytest.mark.django_db
    def test_user_activated(self):
        token = Token.objects.create(account=self.account, type=Token.ACTIVATION)

        account = Account.objects.get(id=self.account.id)

        assert not account.active

        response = self.client.get(
            reverse('account-activation'),
            data={'token': token.token}
        )

        updated_account = Account.objects.get(id=self.account.id)

        assert_that(response.status_code, equal_to(status.HTTP_200_OK))
        assert_that(updated_account.active)
