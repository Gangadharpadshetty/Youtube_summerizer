from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.models.video import video


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # CREATE
    # -----------------------------
    def create_video(
        self,
        video_id: str,
        encrypted_transcript: str,
        language: str
    ) -> video:

        video = video(
            video_id=video_id,
            encrypted_transcript=encrypted_transcript,
            language=language
        )

        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)

        return video

    # -----------------------------
    # READ
    # -----------------------------
    def get_by_video_id(self, video_id: str) -> Optional[video]:

        stmt = select(video).where(video.video_id == video_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    # -----------------------------
    # EXISTS CHECK
    # -----------------------------
    def exists(self, video_id: str) -> bool:

        stmt = select(video.id).where(video.video_id == video_id)
        result = self.db.execute(stmt).first()
        return result is not None