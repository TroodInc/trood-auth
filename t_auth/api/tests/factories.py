import uuid

import factory

from t_auth.api.domain.factories import AccountFactory as DomainAccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole


class AccountFactory(factory.DjangoModelFactory):
    login = factory.Sequence(lambda n: 'account#{}'.format(n))
    pwd_hash = ''

    unique_token = ''
    current_session = ''
    status = Account.STATUS_ACTIVE

    @factory.post_generation
    def pwd_hash(self, create, extracted, **kwargs):
        self._password = uuid.uuid4().hex
        self.unique_token = DomainAccountFactory._create_token()
        if create:
            self.pwd_hash = AuthenticationService.get_password_hash(self._password, self.unique_token)
            self.save()

    class Meta:
        model = Account


class AccountRoleFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Role#{}'.format(n))
    status = AccountRole.STATUS_ACTIVE

    class Meta:
        model = AccountRole
