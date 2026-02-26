from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.api.process_video import router as process_video
from app.api.retrieve_chunks import router as retrieve_chunks_router



app = FastAPI(
    title="YouTube RAG Backend API",
    version="3.0.0",
    description="Storage and retrieval layer for OpenClaw YouTube assistant"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
# app.include_router(health_router)
app.include_router(process_video)
app.include_router(retrieve_chunks_router)