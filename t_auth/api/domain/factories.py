import hashlib
import uuid

from t_auth.api.domain.services import AuthenticationService
from t_auth.api.models import Account


class AccountFactory:

    @classmethod
    def _create_token(cls):
        """
        Creates unique token for an account
        """
        target_str = 'acct' + uuid.uuid4().hex
        return hashlib.sha256(target_str.encode('utf-8')).hexdigest()