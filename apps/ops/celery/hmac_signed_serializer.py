import hmac
import hashlib
import pickle
import os
import socket
from kombu.serialization import register

_local_secret_key = os.environ.get('MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY', 'default_hmac_signed_serializer_secret_key:' + os.getenv('MAXKB_VERSION', socket.gethostname()))
try:
    from xpack import get_md5
    _local_secret_key = get_md5()
except ImportError:
    pass

def secure_dumps(obj):
    data = pickle.dumps(obj)
    signature = hmac.new(_local_secret_key.encode(), data, hashlib.sha256).digest()
    return signature + data

def secure_loads(signed_data):
    if len(signed_data) < 32:
        raise ValueError("Invalid signed data packet")
    signature = signed_data[:32]
    payload = signed_data[32:]
    expected_signature = hmac.new(_local_secret_key.encode(), payload, hashlib.sha256).digest()
    if hmac.compare_digest(signature, expected_signature):
        return pickle.loads(payload)
    else:
        raise ValueError("Security Alert: Task signature mismatch! Potential tampering detected.")

def register_hmac_signed_serializer():
    register(
        'hmac_signed_serializer',
        secure_dumps,
        secure_loads,
        content_type='application/x-python-hmac-signed-serialize',
        content_encoding='binary'
    )