from django.db import models

from t_auth.two_factor_auth.domain.constants import SECOND_AUTH_FACTOR_TYPE


class SecondAuthFactor(models.Model):
    account = models.ForeignKey('api.Account', related_name='second_auth_factors')
    type = models.CharField(max_length=255, choices=SECOND_AUTH_FACTOR_TYPE.CHOICES)

    factor_id = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)


class IntermediateToken(models.Model):
    token = models.CharField(max_length=32, null=False)
    account = models.ForeignKey('api.Account')
    second_factor_id = models.CharField(max_length=255)
    expire = models.DateTimeField(null=False)
