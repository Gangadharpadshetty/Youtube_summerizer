from cryptography.fernet import Fernet
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.video_repository import VideoRepository

import zlib
from typing import Tuple


class CacheService:
    def __init__(self, repo: VideoRepository, fernet_key: str):
        self.repo = repo
        self.fernet = Fernet(fernet_key.encode())

    def get_or_fetch_transcript(self, db: Session, youtube_url: str) -> Tuple[str, str, bool]:
        """
        Returns tuple (transcript, language, cached)
        """
        try:
            video_id = ys.extract_video_id(youtube_url)
        except HTTPException:
            raise

        # Check cache
        existing = self.repo.get_by_video_id(db, video_id)
        if existing:
            try:
                decrypted_bytes = self.fernet.decrypt(existing.transcript_encrypted.encode())
                # Try to decompress; fall back to plain text if not compressed
                try:
                    decompressed = zlib.decompress(decrypted_bytes)
                    decrypted = decompressed.decode()
                except zlib.error:
                    decrypted = decrypted_bytes.decode()
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to decrypt cached transcript")
            return decrypted, getattr(existing, "language", "unknown"), True

        # Fetch transcript via youtube service
        cleaned_text, language = ys.fetch_transcript(video_id)

        # Compress, encrypt and store (compressing improves storage and transfer speed)
        try:
            compressed = zlib.compress(cleaned_text.encode())
            encrypted = self.fernet.encrypt(compressed).decode()
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to encrypt transcript")

        # Persist transcript and language
        try:
            self.repo.create(db, video_id, encrypted, language)
        except Exception:
            # If DB write fails, raise 500 so caller knows caching failed
            raise HTTPException(status_code=500, detail="Failed to store transcript in cache")

        return cleaned_text, language, False
