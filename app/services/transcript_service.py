from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)


class TranscriptService:

    @staticmethod
    def fetch(video_id: str) -> tuple[str, str]:
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join(
                [entry["text"] for entry in transcript_data]
            )
            language = transcript_data[0].get("language", "unknown")
            return transcript_text, language

        except TranscriptsDisabled:
            raise ValueError("Transcripts are disabled for this video.")

        except NoTranscriptFound:
            raise ValueError("No transcript found for this video.")

        except Exception as e:
            raise ValueError(f"Transcript fetch failed: {str(e)}")