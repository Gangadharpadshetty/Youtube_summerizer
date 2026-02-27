from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.api.process_video import router as process_video
from app.api.retrieve_chunks import router as retrieve_chunks_router

app = FastAPI(
    title="YouTube Summarizer RAG Backend",
    version="3.0.0",
    description="YouTube transcript processing, summarization and Q&A retrieval layer for OpenClaw"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(process_video)
app.include_router(retrieve_chunks_router)

# Startup banner
@app.on_event("startup")
async def startup_banner():
    print("""
 __  __            _______       _          
 \ \ \ \          |__   __|     | |         
  \ \ \ \            | |_   _  | |__   ___ 
   \ \ \ \           | | | | | | '_ \ / _ \\
    \_\_\_\          |_| |_,_| |_.__/ \___/
                                            
  YouTube Summarizer v3.0.0 — Running on http://0.0.0.0:8000
  Docs → http://localhost:8000/docs
    """)