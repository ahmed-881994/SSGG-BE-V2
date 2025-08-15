import base64
import hashlib
import secrets
from typing import Optional


def get_password_hash(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password using PBKDF2 with SHA-256.
    
    Args:
        password (str): The plain text password to hash.
        salt (str, optional): The salt to use. If None, generates a new one.
        
    Returns:
        tuple[str, str]: A tuple of (hashed_password, salt).
    """
    if salt is None:
        salt = generate_salt()
    else:
        # Convert hex salt back to bytes if needed
        salt_bytes = bytes.fromhex(salt) if isinstance(salt, str) else salt
    
    # Use PBKDF2 with SHA-256, 100,000 iterations
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                bytes.fromhex(salt), 100000)
    return base64.b64encode(hashed).decode('utf-8'), salt

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The stored hashed password.
        salt (str): The salt used for hashing.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    computed_hash, _ = get_password_hash(plain_password, salt)
    return computed_hash == hashed_password

def generate_salt(length: int = 32) -> str:
    """Generate a cryptographically secure random salt for password hashing.
    
    Args:
        length (int): Length of the salt in bytes. Default is 32.
        
    Returns:
        str: A hex-encoded salt string.
    """
    return secrets.token_hex(length)