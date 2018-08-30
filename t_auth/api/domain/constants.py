from django.utils.translation import ugettext_lazy as _


class TOKEN_TYPE:
    RECOVERY = 'recovery'

    AUTHORIZATION = 'authorization'
    TWO_FACTOR_INTERMEDIATE = '2_fa_intermediate'
    TWO_FACTOR_VERIFICATION = '2_fa_verification'

    CHOICES = (
        (RECOVERY, _('Recovery')),
        (AUTHORIZATION, _('Authorization')),
        (TWO_FACTOR_INTERMEDIATE, _('2fa intermediate')),
        (TWO_FACTOR_VERIFICATION, _('Second factor verification')),
    )
