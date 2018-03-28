import uuid

import factory

from t_auth.api.constants import OBJECT_STATUS, PERMISSION_TARGET
from t_auth.api.domain.factories import AccountFactory as DomainAccountFactory
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountPermission, AccountRole, Endpoint


class AccountFactory(factory.DjangoModelFactory):
    login = factory.Sequence(lambda n: 'account#{}'.format(n))
    pwd_hash = ''

    unique_token = ''
    current_session = ''
    status = OBJECT_STATUS['active']

    @factory.post_generation
    def pwd_hash(self, create, extracted, **kwargs):
        self._password = uuid.uuid4().hex
        self.unique_token = DomainAccountFactory._create_token()
        if create:
            self.pwd_hash = AuthenticationService.get_password_hash(self._password, self.unique_token)
            self.save()

    class Meta:
        model = Account


class EndpointFactory(factory.DjangoModelFactory):
    url = factory.Sequence(lambda n: '/api/v1.0/{}'.format(uuid.uuid4().hex))

    class Meta:
        model = Endpoint


class AccountPermissionFactory(factory.DjangoModelFactory):
    endpoint = factory.SubFactory(EndpointFactory)
    method = factory.Sequence(lambda n: 'method#{}'.format(n))
    target_objects = PERMISSION_TARGET['own_objects']

    class Meta:
        model = AccountPermission


class AccountRoleFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Role#{}'.format(n))
    status = OBJECT_STATUS['active']

    class Meta:
        model = AccountRole
