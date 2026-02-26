from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, key: str):
        self.fernet = Fernet(key)

    def encrypt(self, text: str) -> str:
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        return self.fernet.decrypt(encrypted_text.encode()).decode()