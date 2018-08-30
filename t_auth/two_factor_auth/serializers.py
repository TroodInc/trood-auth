from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, fields

from t_auth.api.models import Account
from t_auth.tools.drf.fields import PhoneField
from t_auth.two_factor_auth.domain.factories import IntermediateTokenFactory
from t_auth.two_factor_auth.models import SecondAuthFactor, IntermediateToken


class UniqueValidator(object):
    def __init__(self, factor_type):
        self.factor_type = factor_type

    def __call__(self, value):
        if SecondAuthFactor.objects.filter(factor_id=value).count() > 0:
            raise serializers.ValidationError(_('Account with that {} already exists'.format(self.factor_type)))


class ExistingAccount(object):

    def __call__(self, value):
        if Account.objects.filter(login=value).count() == 0:
            raise serializers.ValidationError(_('Account with that email does not exist'))


class PhoneFactorSerializer(serializers.ModelSerializer):
    login = fields.EmailField(validators=[ExistingAccount()], write_only=True)
    phone = PhoneField(validators=[UniqueValidator(factor_type=_("phone"))], write_only=True)
    token = serializers.CharField(read_only=True)

    def _get_account(self, email):
        return Account.objects.get(login=email)

    def save(self, **kwargs):
        self.instance = IntermediateTokenFactory.factory(
            account=self._get_account(self.validated_data['login']),
            second_factor_id=self.validated_data['phone']
        )
        return self.instance

    class Meta:
        fields = ('login', 'phone', 'token')
        model = IntermediateToken
