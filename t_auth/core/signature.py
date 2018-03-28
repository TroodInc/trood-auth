# encoding: utf-8
"""
Auth Service Backend

Utility methods (such as signing messages etc)
"""
import rsa
import time
import json
import base64


def sign_json(raw_json, privkey):
    """
    Signs json with target private key
    """
    raw_json['ts'] = time.time()
    x_str = json.dumps(raw_json).encode('utf-8')

    raw_json['sign'] = base64.urlsafe_b64encode(
        rsa.sign(x_str, privkey, 'SHA-1')
    )
    return raw_json


def check_json(raw_json, pubkey):
    """
    Checks json signature using target public key
    """
    ts = raw_json.get('ts', None)
    sign = base64.urlsafe_b64decode(raw_json.pop('sign', ''))

    x_str = json.dumps(raw_json).encode('utf-8')
    ret = rsa.verify(x_str, sign, pubkey)

    return ret
