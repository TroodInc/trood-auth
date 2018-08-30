from django.utils.translation import ugettext_lazy as _


class TOKEN_TYPE:
    RECOVERY = 'recovery'
    AUTHORIZATION = 'authorization'

    CHOICES = (
        (RECOVERY, _('Recovery')),
        (AUTHORIZATION, _('Authorization')),
    )
