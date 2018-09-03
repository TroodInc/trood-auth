from django.utils.translation import ugettext_lazy as _


class TWO_FACTOR_TYPE:
    SMS = 'SMS'

    CHOICES = (
        (SMS, _('SMS')),
    )


class INTERMEDIATE_TOKEN_VERIFICATION_TYPE:
    BINDING = 1
    AUTHORIZATION = 2

    CHOICES = (
        (BINDING, 'Binding'),
        (AUTHORIZATION, 'Authorization'),
    )


class MESSAGES:
    TWO_FACTOR_BIND_REQUIRED = _('2fa binding is required for account')
    TOKEN_IS_INVALID = _('Provided token is not valid')
    TOKEN_HAS_BEEN_SENT = _('2fa token has been sent')
