from django.conf import settings
from rest_framework.generics import CreateAPIView

from t_auth.two_factor_auth.domain.constants import SECOND_AUTH_FACTOR_TYPE
from t_auth.two_factor_auth.serializers import PhoneFactorSerializer


class BindSecondAuthFactorApiView(CreateAPIView):
    serializer_classes = {
        SECOND_AUTH_FACTOR_TYPE.PHONE: PhoneFactorSerializer
    }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_classes[settings.TWO_FACTOR.AUTH_TYPE]
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
