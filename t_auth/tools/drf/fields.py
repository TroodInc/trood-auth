import re

from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField


class PhoneField(CharField):
    def run_validation(self, data=None):
        if data is not None:
            if len(re.sub(r'\D', u'', data)[-11:]) < 11:
                raise ValidationError("Phone has invalid length")

        return super(PhoneField, self).run_validation(data)

    def to_internal_value(self, data):
        return re.sub(r'\D', u'', data)[-11:]
