from django.utils.translation import ugettext_lazy as _


class TWO_FACTOR_TYPE:
    PHONE = 'PHONE'

    CHOICES = (
        (PHONE, _('Phone')),
    )
