import datetime
import uuid

from django.conf import settings

from t_auth.api.models import Account
from t_auth.two_factor_auth.models import IntermediateToken


class IntermediateTokenFactory:
    @classmethod
    def factory(cls, account: Account, second_factor_id: str):
        return IntermediateToken.objects.create(
            second_factor_id=second_factor_id,
            account=account,
            expire=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                minutes=settings.TWO_FACTOR.INTERMEDIATE_TOKEN_TTL),
            token=uuid.uuid4().hex[:6]
        )
