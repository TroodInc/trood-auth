from django.utils.translation import ugettext_lazy as _


class SECOND_AUTH_FACTOR_TYPE:
    PHONE = 'PHONE'

    CHOICES = (
        (PHONE, _('Phone')),
    )
