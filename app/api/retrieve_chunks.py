from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RetrieveChunksRequest, RetrieveChunksResponse
from app.services.rag_service import retrieve_relevant_chunks

router = APIRouter(prefix="/retrieve_chunks", tags=["Retrieval"])


@router.post("/", response_model=RetrieveChunksResponse)
def retrieve_chunks(request: RetrieveChunksRequest, db: Session = Depends(get_db)):

    service = retrieve_relevant_chunks(db)

    try:
        chunks = service.retrieve(
            video_id=request.video_id,
            question=request.question,
            top_k=request.top_k
        )

        return RetrieveChunksResponse(
            video_id=request.video_id,
            chunks=chunks
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")