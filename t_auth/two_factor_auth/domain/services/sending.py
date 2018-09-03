from t_auth.two_factor_auth.models import IntermediateToken


class SmsSendingService:
    @classmethod
    def send(cls, token: IntermediateToken):
        pass
