import datetime
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from t_auth.api.models import Token
from t_auth.api.serializers import VerificationSerializer


class VerifyTokenView(APIView):
    """
    Provides external API /auth method
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        return Response(VerificationSerializer(request.user.account).data)


class InvalidateTokenView(APIView):
    """
    Provides service link for cleaning up tokens
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        if 'all' in request.data:
            count, _ = Token.objects.all().delete()
        else:
            now = datetime.datetime.now(tz=timezone.utc)
            count, _ = Token.objects.filter(expire__lt=now).delete()

        return Response({"tokens_removed": count})
