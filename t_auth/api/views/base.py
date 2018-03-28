# encoding: utf-8
"""
Auth Service Backend

Public endpoints (login/logout, authentication, two-factor login, registration)
"""
import rsa
from rest_framework import viewsets

from t_auth.api.errors import ERROR_TYPES
from t_auth.core import signature


class BaseViewSet(viewsets.ViewSet):
    @staticmethod
    def pack_json(raw_json):
        # TODO: Replace this dummy key generation with proper key storage
        # privkey retrieval
        ret = raw_json
        (pub_key, priv_key) = rsa.newkeys(1024)
        return signature.sign_json(ret, priv_key)

    @staticmethod
    def not_implemented():
        # returns default 'not implemented' error
        return BaseViewSet.error_json('not_implemented')

    @staticmethod
    def error_json(message_code):
        ret = {
            'error': {
                'code': message_code,
                'message': ERROR_TYPES[message_code]
            }
        }
        return ret
