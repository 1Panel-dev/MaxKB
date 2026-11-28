import hmac
import hashlib
import pickle
import os
import uuid_utils.compat as uuid
from kombu.serialization import register

_local_secret_key = (
    os.environ.get('MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY')
    or os.environ.get('MAXKB_SECRET_KEY')
    or str(uuid.uuid7())
)
try:
    from xpack import get_md5
    _local_secret_key = get_md5()
except ImportError:
    pass


def _secret_key_bytes():
    if isinstance(_local_secret_key, bytes):
        return _local_secret_key
    return str(_local_secret_key).encode()


def secure_dumps(obj):
    data = pickle.dumps(obj)
    signature = hmac.new(_secret_key_bytes(), data, hashlib.sha256).digest()
    return signature + data

def secure_loads(signed_data):
    if len(signed_data) < 32:
        raise ValueError("Invalid signed data packet")
    signature = signed_data[:32]
    payload = signed_data[32:]
    expected_signature = hmac.new(_secret_key_bytes(), payload, hashlib.sha256).digest()
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