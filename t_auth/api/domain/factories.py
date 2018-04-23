import hashlib
import uuid

from t_auth.api.constants import OBJECT_STATUS
from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account, AccountRole


class AccountFactory:

    @classmethod
    def _create_token(cls):
        """
        Creates unique token for an account
        """
        target_str = 'acct' + uuid.uuid4().hex
        return hashlib.sha256(target_str.encode('utf-8')).hexdigest()

    @classmethod
    def factory(cls, login, password, status=OBJECT_STATUS.ACTIVE, role=None):
        account = Account()
        account.login = login
        account.unique_token = cls._create_token()
        account.pwd_hash = AuthenticationService.get_password_hash(password, account.unique_token)
        account.status = status
        account.save()

        return account
