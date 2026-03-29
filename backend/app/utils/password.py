import hashlib
import secrets

def hash_password(password: str) -> str:
    """密码哈希"""
    salt = secrets.token_hex(8)
    return salt + ':' + hashlib.sha256((salt + password).encode()).hexdigest()

def check_password(password: str, hashed: str) -> bool:
    """验证密码"""
    if ':' not in hashed:
        return False
    salt, h = hashed.split(':')
    return h == hashlib.sha256((salt + password).encode()).hexdigest()