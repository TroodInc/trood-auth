from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from t_auth.api.models import Account
from t_auth.two_factor_auth.domain.constants import MESSAGES
from t_auth.two_factor_auth.domain.services import IntermediateTokenValidationService
from t_auth.two_factor_auth.models import AuthFactor


class UniqueValidator(object):
    def __init__(self, factor_type):
        self.factor_type = factor_type

    def __call__(self, value):
        if AuthFactor.objects.filter(factor_id=value).count() > 0:
            raise serializers.ValidationError(_('Account with that {} already exists'.format(self.factor_type)))


class LoginExistingAccountValidator(object):
    def __call__(self, value):
        if Account.objects.filter(login=value).count() == 0:
            raise serializers.ValidationError(_('Account with that email does not exist'))


class IntermediateTokenValidator:
    def __init__(self, verification_type):
        self.verification_type = verification_type

    def __call__(self, values):
        intermediate_token = IntermediateTokenValidationService.validate(
            factor_type=settings.TWO_FACTOR_AUTH_TYPE,
            factor_id=values['factor_id'],
            token=values['temporary_token'],
            verification_type=self.verification_type
        )
        if not intermediate_token:
            raise ValidationError({"intermediate_token": MESSAGES.TOKEN_IS_INVALID})
        setattr(self, 'intermediate_token', intermediate_token)
