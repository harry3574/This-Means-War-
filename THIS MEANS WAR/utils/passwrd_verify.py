
import hashlib
import secrets

def verify_password(stored_salt: str, stored_hash: str, password: str) -> bool:
        """Verify password against stored hash"""
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            stored_salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(new_hash, stored_hash)

def hash_password(password: str) -> tuple:
        """Generate salt and hash for password"""
        salt = secrets.token_hex(16)
        hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return salt, hash