from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, fields

from t_auth.api.domain.constants import TOKEN_TYPE
from t_auth.api.models import Account, Token
from t_auth.api.serializers import AuthorizationTokenSerializer
from t_auth.tools.drf.fields import PhoneField
from t_auth.two_factor_auth.domain.constants import INTERMEDIATE_TOKEN_VERIFICATION_TYPE
from t_auth.two_factor_auth.domain.factories import IntermediateTokenFactory, SecondAuthFactorFactory
from t_auth.two_factor_auth.domain.services import IntermediateTokenValidationService
from t_auth.two_factor_auth.models import IntermediateToken
from t_auth.two_factor_auth.validators import LoginExistingAccountValidator, UniqueValidator, IntermediateTokenValidator


class PhoneFactorBindingSerializer(serializers.ModelSerializer):
    login = fields.EmailField(validators=[LoginExistingAccountValidator()], write_only=True)
    factor_id = PhoneField(validators=[UniqueValidator(factor_type=_("phone"))], write_only=True)
    temporary_token = serializers.CharField(read_only=True, source='token')

    def _get_account(self, email):
        return Account.objects.get(login=email)

    def save(self, **kwargs):
        self.instance = IntermediateTokenFactory.factory(
            account=self._get_account(self.validated_data['login']),
            factor_id=self.validated_data['factor_id'],
            factor_type=settings.TWO_FACTOR_AUTH_TYPE,
            verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.BINDING
        )
        return self.instance

    class Meta:
        fields = ('login', 'factor_id', 'temporary_token')
        model = IntermediateToken


class BindingIntermediateTokenVerificationSerializer(AuthorizationTokenSerializer):
    # token
    temporary_token = serializers.CharField(write_only=True)
    factor_id = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        intermediate_token = IntermediateToken.objects.get(
            token=self.validated_data['temporary_token'],
            used=False,
            verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.BINDING
        )
        SecondAuthFactorFactory.factory(
            account=intermediate_token.account,
            factor_type=intermediate_token.factor_type,
            factor_id=intermediate_token.factor_id
        )
        self.instance = Token.objects.create(
            account=intermediate_token.account,
            type=TOKEN_TYPE.AUTHORIZATION
        )
        IntermediateTokenValidationService.invalidate(intermediate_token)
        return self.instance

    class Meta:
        fields = AuthorizationTokenSerializer.Meta.fields + ('temporary_token', 'factor_id')
        model = Token
        validators = [IntermediateTokenValidator(INTERMEDIATE_TOKEN_VERIFICATION_TYPE.BINDING)]


class AuthorizationIntermediateTokenVerificationSerializer(BindingIntermediateTokenVerificationSerializer):
    def save(self, **kwargs):
        intermediate_token = IntermediateToken.objects.get(
            token=self.validated_data['temporary_token'],
            used=False,
            verification_type=INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION
        )
        self.instance = Token.objects.create(
            account=intermediate_token.account,
            type=TOKEN_TYPE.AUTHORIZATION
        )
        IntermediateTokenValidationService.invalidate(intermediate_token)
        return self.instance

    class Meta:
        fields = AuthorizationTokenSerializer.Meta.fields + ('temporary_token', 'factor_id')
        model = Token
        validators = [IntermediateTokenValidator(INTERMEDIATE_TOKEN_VERIFICATION_TYPE.AUTHORIZATION)]
