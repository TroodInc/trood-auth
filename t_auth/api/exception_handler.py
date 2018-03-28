from rest_framework.response import Response


def custom_exception_handler(exc, context):
    detail = getattr(exc, 'detail', None) or exc.args[0] if hasattr(exc, 'args') else None
    return Response({'status': 'FAIL', 'error': detail})
