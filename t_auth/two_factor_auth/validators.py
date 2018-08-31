from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from t_auth.api.models import Account
from t_auth.two_factor_auth.domain.services import IntermediateTokenValidationService
from t_auth.two_factor_auth.models import SecondAuthFactor


class UniqueValidator(object):
    def __init__(self, factor_type):
        self.factor_type = factor_type

    def __call__(self, value):
        if SecondAuthFactor.objects.filter(factor_id=value).count() > 0:
            raise serializers.ValidationError(_('Account with that {} already exists'.format(self.factor_type)))


class LoginExistingAccountValidator(object):
    def __call__(self, value):
        if Account.objects.filter(login=value).count() == 0:
            raise serializers.ValidationError(_('Account with that email does not exist'))


class IntermediateTokenValidator:

    def __call__(self, values):
        intermediate_token = IntermediateTokenValidationService.validate(
            factor_type=settings.TWO_FACTOR_AUTH_TYPE,
            factor_id=values['factor_id'],
            token=values['temporary_token']
        )
        if not intermediate_token:
            raise ValidationError({"intermediate_token": "Provided token is not valid"})
        setattr(self, 'intermediate_token', intermediate_token)
