from django.db import models

from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE, INTERMEDIATE_TOKEN_VERIFICATION_TYPE


class AuthFactor(models.Model):
    account = models.ForeignKey('api.Account', related_name='auth_factors')
    type = models.CharField(max_length=255, choices=TWO_FACTOR_TYPE.CHOICES)

    factor_id = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)


class IntermediateToken(models.Model):
    token = models.CharField(max_length=32, null=False)
    verification_type = models.IntegerField(choices=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.CHOICES)
    account = models.ForeignKey('api.Account')
    factor_id = models.CharField(max_length=255)
    factor_type = models.CharField(max_length=255, choices=TWO_FACTOR_TYPE.CHOICES)
    expire = models.DateTimeField(null=False)
    used = models.BooleanField(default=False)
