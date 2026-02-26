# Database Setup & Schema

## Complete Schema Overview

### Table: `videos`

```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(64) NOT NULL UNIQUE,
    transcript_encrypted TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_videos_video_id ON videos(video_id);
CREATE INDEX idx_videos_created_at ON videos(created_at);
```

### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY, AUTO INCREMENT | Unique identifier |
| `video_id` | VARCHAR(64) | UNIQUE, INDEX | YouTube video ID (11-char code) |
| `transcript_encrypted` | TEXT | NOT NULL | Fernet-encrypted transcript (base64) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP, INDEX | When cached |

## ORM Model

```python
# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(64), unique=True, index=True, nullable=False)
    transcript_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

## Initialization Instructions

### Option 1: Automatic (Python Script)

```bash
cd telegram-youtube-bot
. .venv\Scripts\Activate.ps1
python init_db.py
```

### Option 2: Manual (SQL)

For PostgreSQL on Render:
```sql
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(64) NOT NULL UNIQUE,
    transcript_encrypted TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_video_id ON videos(video_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);
```

For SQLite (local development):
```bash
sqlite3 dev.db < schema.sql
```

### Option 3: FastAPI Auto-Create

Tables are **automatically created** on first server start:

```python
# In app/database.py:
Base.metadata.create_all(engine)
```

Just run the server and it initializes the database:
```bash
uvicorn app.main:app --reload
```

## Pydantic Schemas

Located in `app/schemas.py`:

### TranscriptRequest
```python
{
  "youtube_url": "https://www.youtube.com/watch?v=ABCDEFGHIJK"
}
```

### TranscriptResponse
```python
{
  "video_id": "ABCDEFGHIJK",
  "language": "en",
  "transcript": "Hello world...",
  "cached": true
}
```

### VideoReadSchema
```python
{
  "id": 1,
  "video_id": "ABCDEFGHIJK",
  "created_at": "2025-02-25T10:30:00Z"
}
```

## SQLAlchemy Configuration

### Database URL Format

**PostgreSQL (Render Production)**:
```
postgresql://username:password@host:port/database
```

**SQLite (Local Development)**:
```
sqlite:///./dev.db
```

**MySQL**:
```
mysql+pymysql://username:password@host:port/database
```

### Connection Pooling (app/database.py)

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Persistent connections
    max_overflow=10,       # Additional temp connections
    pool_pre_ping=True,    # Validate before use
    connect_args={}        # Driver-specific options
)
```

## Sample Queries

### Check if video is cached
```python
from app.repositories.video_repository import VideoRepository
from app.database import SessionLocal

repo = VideoRepository()
db = SessionLocal()
video = repo.get_by_video_id(db, "ABCDEFGHIJK")
if video:
    print("Cached!")
db.close()
```

### Store encrypted transcript
```python
from cryptography.fernet import Fernet
from app.repositories.video_repository import VideoRepository

repo = VideoRepository()
encrypted = Fernet(key).encrypt(transcript.encode()).decode()
repo.create(db, "ABCDEFGHIJK", encrypted)
```

### Raw SQL Queries (if needed)

```sql
-- Count cached transcripts
SELECT COUNT(*) FROM videos;

-- Find oldest cached transcript
SELECT * FROM videos ORDER BY created_at ASC LIMIT 1;

-- Delete cached transcript
DELETE FROM videos WHERE video_id = 'ABCDEFGHIJK';

-- Get all videos cached after a date
SELECT * FROM videos WHERE created_at > '2025-02-20' ORDER BY created_at DESC;
```

## Environment Variables

Create `.env` file (or set in Render dashboard):

```env
# Database (required for production)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Encryption key (required)
FERNET_KEY=<base64-key-from-Fernet.generate_key()>

# Optional
TELEGRAM_TOKEN=your_token
YOUTUBE_API_KEY=your_key
```

Generate FERNET_KEY:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Testing

Run all tests (including cache service tests):
```bash
pytest tests/ -v
```

Run only cache tests:
```bash
pytest tests/test_cache_service.py -v
```

## Deployment to Render

1. **Create PostgreSQL Database** in Render (free tier available)
2. **Set Environment Variables**:
   - `DATABASE_URL` → connection string from Render postgres
   - `FERNET_KEY` → generated encryption key
3. **Push to GitHub**
4. **Connect Git Repo** to Render Web Service
5. **Tables auto-create** on first deployment

## Troubleshooting

### Table doesn't exist error
```bash
# Manually create:
python -c "from app.database import Base, engine; from app.models import Video; Base.metadata.create_all(engine)"
```

### Connection refused
- Check `DATABASE_URL` is correct
- For Render: wait for database to be ready (can take 1-2 minutes)
- For PostgreSQL: ensure psycopg2-binary is installed

### Encryption errors
- Verify `FERNET_KEY` is valid base64 and 44 chars long
- Regenerate if corrupted: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## Files Created

- `app/models.py` - ORM models (Video)
- `app/schemas.py` - Pydantic request/response models
- `app/database.py` - SQLAlchemy engine & session
- `app/repositories/video_repository.py` - Repository pattern
- `app/services/cache_service.py` - Caching logic
- `init_db.py` - Table creation script
- `setup.py` - Full setup script
- `schema.sql` - SQL schema reference
- `.env.example` - Environment template
