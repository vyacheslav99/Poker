import hashlib


def encrypt(value: str) -> str:
    return hashlib.sha224(value.encode()).hexdigest()
