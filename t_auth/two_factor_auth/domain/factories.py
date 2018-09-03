import datetime
import uuid

import pytz
from django.conf import settings

from t_auth.api.models import Account
from t_auth.two_factor_auth.models import IntermediateToken, AuthFactor


class IntermediateTokenFactory:
    @classmethod
    def factory(cls, account: Account, factor_id: str, factor_type: str, verification_type: int):
        if settings.TWO_FACTOR_MOCK_MODE:
            token = '000000'
            IntermediateToken.objects.filter(token=token).delete()
        else:
            token = uuid.uuid4().hex[:6]
        return IntermediateToken.objects.create(
            factor_id=factor_id,
            account=account,
            expire=datetime.datetime.now(tz=pytz.UTC) + datetime.timedelta(
                minutes=settings.TWO_FACTOR_INTERMEDIATE_TOKEN_TTL),
            token=token,
            factor_type=factor_type,
            verification_type=verification_type
        )


class SecondAuthFactorFactory:
    @classmethod
    def factory(cls, account: Account, factor_type: str, factor_id) -> AuthFactor:
        return AuthFactor.objects.create(
            account=account,
            type=factor_type,
            factor_id=factor_id
        )
