-- YouTube Transcript Caching Schema
-- This SQL is auto-generated from SQLAlchemy ORM models and is provided for reference only.
-- For PostgreSQL (production):

CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(64) NOT NULL UNIQUE,
    transcript_encrypted TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on video_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_videos_video_id ON videos(video_id);

-- Index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);

-- Table Description:
-- 
-- id: Auto-incrementing primary key
-- video_id: YouTube video ID (unique, indexed for O(1) lookups)
-- transcript_encrypted: Fernet-encrypted transcript (UTF-8 base64 encoded)
-- created_at: Timestamp when transcript was cached (server-side default)

-- Example encrypted transcript (actual value will be much longer):
-- gAAAAABlXoCDv8C...base64...==

-- SAMPLE QUERIES:

-- Check if a video is cached
SELECT transcript_encrypted, created_at FROM videos WHERE video_id = 'ABCDEFGHIJK';

-- Get all cached transcripts with pagination
SELECT id, video_id, created_at FROM videos ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- Delete a cached transcript
DELETE FROM videos WHERE video_id = 'ABCDEFGHIJK';

-- Get cache statistics
SELECT COUNT(*) as total_cached, 
       MIN(created_at) as oldest_cache,
       MAX(created_at) as newest_cache
FROM videos;
