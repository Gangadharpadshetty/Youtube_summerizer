
from cryptography.fernet import Fernet

def encrypt_text(fernet: Fernet, text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(fernet: Fernet, encrypted_text: str) -> str:
    return fernet.decrypt(encrypted_text.encode()).decode()