from django.conf import settings
from rest_framework.generics import CreateAPIView

from t_auth.two_factor_auth.domain.constants import TWO_FACTOR_TYPE
from t_auth.two_factor_auth.serializers import PhoneFactorBindingSerializer, IntermediateTokenVerificationSerializer


class BindSecondAuthFactorApiView(CreateAPIView):
    serializer_classes = {
        TWO_FACTOR_TYPE.PHONE: PhoneFactorBindingSerializer
    }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_classes[settings.TWO_FACTOR_AUTH_TYPE]
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class VerifyIntermediateTokenApiView(CreateAPIView):
    serializer_class = IntermediateTokenVerificationSerializer
