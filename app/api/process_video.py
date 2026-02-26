from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.process_video import ProcessVideoRequest, ProcessVideoResponse
from app.services.video_service import VideoService

router = APIRouter(prefix="/process_video", tags=["Video"])


@router.post("/", response_model=ProcessVideoResponse)
def process_video(request: ProcessVideoRequest, db: Session = Depends(get_db)):

    service = VideoService(db)

    try:
        result = service.process_video(
            youtube_url=request.youtube_url,
            video_id=request.video_id,
            language=request.language
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")