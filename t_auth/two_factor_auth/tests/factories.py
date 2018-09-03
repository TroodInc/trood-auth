import factory

from t_auth.two_factor_auth.models import AuthFactor


class AuthFactorFactory(factory.DjangoModelFactory):
    factor_id = '79999999999'

    class Meta:
        model = AuthFactor
