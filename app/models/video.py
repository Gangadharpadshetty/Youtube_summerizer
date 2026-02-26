from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database.base import Base


class video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), unique=True, nullable=False, index=True)
    encrypted_transcript = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())