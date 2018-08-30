import factory

from t_auth.two_factor_auth.models import SecondAuthFactor


class SecondAuthFactorFactory(factory.DjangoModelFactory):
    class Meta:
        model = SecondAuthFactor
