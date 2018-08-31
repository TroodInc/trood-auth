import datetime

import pytz
from django.conf import settings

from t_auth.two_factor_auth.models import IntermediateToken, SecondAuthFactor


class IntermediateTokenValidationService:
    @classmethod
    def validate(cls, factor_type, factor_id, token):
        try:
            return IntermediateToken.objects.get(
                token=token,
                factor_id=factor_id,
                factor_type=factor_type,
                expire__gte=datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(
                    minutes=settings.TWO_FACTOR_INTERMEDIATE_TOKEN_TTL),
                used=False
            )
        except IntermediateToken.DoesNotExist:
            return None

    @classmethod
    def invalidate(cls, token: IntermediateToken):
        token.used = True
        token.save(update_fields=['used'])
        return token


class AccountValidationService:
    @classmethod
    def two_factor_is_enabled_for_account(cls, account):
        return SecondAuthFactor.objects.filter(account=account).count() > 0
