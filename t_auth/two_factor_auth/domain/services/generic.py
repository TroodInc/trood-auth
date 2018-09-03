import datetime

import pytz

from t_auth.api.models import Account
from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE, INTERMEDIATE_TOKEN_VERIFICATION_TYPE
from t_auth.two_factor_auth.domain.factories import IntermediateTokenFactory
from t_auth.two_factor_auth.domain.services.sending import SmsSendingService
from t_auth.two_factor_auth.models import IntermediateToken, AuthFactor


class IntermediateTokenValidationService:
    @classmethod
    def validate(cls, factor_type, factor_id, token, verification_type: int):
        try:
            return IntermediateToken.objects.get(
                token=token,
                factor_id=factor_id,
                factor_type=factor_type,
                expire__gte=datetime.datetime.now(tz=pytz.UTC),
                used=False,
                verification_type=verification_type
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
        return AuthFactor.objects.filter(account=account).count() > 0


class AccountAuthService:
    FACTOR_SENDING_SERVICES = {
        TWO_FACTOR_TYPE.SMS: SmsSendingService
    }

    @classmethod
    def _get_auth_factor(cls, account: Account):
        return AuthFactor.objects.filter(account=account).first()

    @classmethod
    def initiate(cls, account: Account):
        """
        Generate temporary token and send it to user via corresponding method
        :param account:
        """
        auth_factor = cls._get_auth_factor(account)
        intermediate_token = IntermediateTokenFactory.factory(
            account=auth_factor.account,
            factor_id=auth_factor.factor_id,
            factor_type=auth_factor.type,
            verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
        )
        cls.FACTOR_SENDING_SERVICES[auth_factor.type].send(intermediate_token)
        return intermediate_token
