from django.utils.translation import ugettext_lazy as _


class TWO_FACTOR_TYPE:
    PHONE = 'PHONE'

    CHOICES = (
        (PHONE, _('Phone')),
    )


class EXCEPTIONS:
    TWO_FACTOR_BIND_REQUIRED = _('2fa binding is required for account')
    TOKEN_IS_INVALID = _('Provided token is not valid')
