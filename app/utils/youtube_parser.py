
import re
import pytest


# ── function under test ────────────────────────────────────────────────────────

def extract_video_id(youtube_url: str) -> str:
    """Extracts video ID from YouTube URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"youtube\.com\/embed\/([0-9A-Za-z_-]{11})",
        r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL")


# ── test cases ─────────────────────────────────────────────────────────────────

VIDEO_ID = "dQw4w9WgXcQ"  # canonical test video ID (11 chars)


class TestStandardWatchURL:
    """youtube.com/watch?v=VIDEO_ID"""

    def test_basic_watch_url(self):
        url = f"https://www.youtube.com/watch?v={VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_watch_url_without_https(self):
        url = f"youtube.com/watch?v={VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_watch_url_without_www(self):
        url = f"https://youtube.com/watch?v={VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_watch_url_with_extra_params(self):
        url = f"https://www.youtube.com/watch?v={VIDEO_ID}&t=30&list=PL123"
        assert extract_video_id(url) == VIDEO_ID

    def test_watch_url_with_timestamp(self):
        url = f"https://www.youtube.com/watch?v={VIDEO_ID}&t=120s"
        assert extract_video_id(url) == VIDEO_ID


class TestShortURL:
    """youtu.be/VIDEO_ID"""

    def test_basic_short_url(self):
        url = f"https://youtu.be/{VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_short_url_without_https(self):
        url = f"youtu.be/{VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_short_url_with_params(self):
        url = f"https://youtu.be/{VIDEO_ID}?t=30"
        assert extract_video_id(url) == VIDEO_ID


class TestEmbedURL:
    """youtube.com/embed/VIDEO_ID"""

    def test_basic_embed_url(self):
        url = f"https://www.youtube.com/embed/{VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_embed_url_with_params(self):
        url = f"https://www.youtube.com/embed/{VIDEO_ID}?autoplay=1"
        assert extract_video_id(url) == VIDEO_ID


class TestShortsURL:
    """youtube.com/shorts/VIDEO_ID"""

    def test_basic_shorts_url(self):
        url = f"https://www.youtube.com/shorts/{VIDEO_ID}"
        assert extract_video_id(url) == VIDEO_ID

    def test_shorts_url_with_params(self):
        url = f"https://www.youtube.com/shorts/{VIDEO_ID}?feature=share"
        assert extract_video_id(url) == VIDEO_ID


class TestVideoIDCharacters:
    """Video ID character validation — must be exactly 11 chars [0-9A-Za-z_-]"""

    def test_video_id_with_hyphens(self):
        # Pattern 1 (v=|/) matches the slash before the ID chars greedily
        # so youtu.be pattern is more reliable for hyphen-heavy IDs
        url = f"https://youtu.be/a-b-c-d-e-fg"
        assert extract_video_id(url) == "a-b-c-d-e-fg"

    def test_video_id_with_underscores(self):
        url = f"https://youtu.be/a_b_c_d_e_fg"
        assert extract_video_id(url) == "a_b_c_d_e_fg"

    def test_video_id_all_numbers(self):
        url = "https://www.youtube.com/watch?v=12345678901"
        assert extract_video_id(url) == "12345678901"

    def test_video_id_mixed_case(self):
        url = "https://www.youtube.com/watch?v=AbCdEfGhIjK"
        assert extract_video_id(url) == "AbCdEfGhIjK"

    def test_returned_id_is_always_11_chars(self):
        url = f"https://www.youtube.com/watch?v={VIDEO_ID}"
        result = extract_video_id(url)
        assert len(result) == 11


class TestInvalidURLs:
    """Invalid URLs must raise ValueError"""

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("")

    def test_random_string_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("not a url at all")

    def test_non_youtube_url_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("https://www.google.com/search?q=hello")

    def test_vimeo_url_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("https://vimeo.com/123456789")

    def test_plain_youtube_homepage_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("https://www.youtube.com")

    def test_short_id_less_than_11_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            extract_video_id("https://www.youtube.com/watch?v=short")