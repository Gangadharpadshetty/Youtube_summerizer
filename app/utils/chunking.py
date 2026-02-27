import pytest
from typing import List
import re


# ── function under test ────────────────────────────────────────────────────────

def chunk_transcript(transcript: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    if not transcript:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >=0 and < chunk_size")

    words = re.findall(r"\S+", transcript)
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    n = len(words)

    while start < n:
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end >= n:
            break
        start = end - overlap

    return chunks


# ── helpers ────────────────────────────────────────────────────────────────────

def make_transcript(word_count: int, word: str = "word") -> str:
    """Generate a transcript with exactly `word_count` words."""
    return " ".join([word] * word_count)


# ── edge cases ─────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_string_returns_empty_list(self):
        assert chunk_transcript("") == []

    def test_none_like_falsy_empty(self):
        # empty string is falsy, treated same as missing
        assert chunk_transcript("   ") == []

    def test_whitespace_only_returns_empty_list(self):
        assert chunk_transcript("    \n\t   ") == []

    def test_single_word(self):
        result = chunk_transcript("hello", chunk_size=10, overlap=2)
        assert result == ["hello"]

    def test_transcript_shorter_than_chunk_size(self):
        transcript = make_transcript(5)
        result = chunk_transcript(transcript, chunk_size=100, overlap=10)
        assert len(result) == 1
        assert result[0] == transcript.strip()

    def test_transcript_exactly_chunk_size(self):
        transcript = make_transcript(10)
        result = chunk_transcript(transcript, chunk_size=10, overlap=2)
        assert len(result) == 1


# ── validation errors ──────────────────────────────────────────────────────────

class TestValidation:

    def test_chunk_size_zero_raises(self):
        with pytest.raises(ValueError, match="chunk_size must be > 0"):
            chunk_transcript("some text", chunk_size=0)

    def test_chunk_size_negative_raises(self):
        with pytest.raises(ValueError, match="chunk_size must be > 0"):
            chunk_transcript("some text", chunk_size=-5)

    def test_overlap_negative_raises(self):
        with pytest.raises(ValueError, match="overlap must be"):
            chunk_transcript("some text", chunk_size=10, overlap=-1)

    def test_overlap_equal_to_chunk_size_raises(self):
        with pytest.raises(ValueError, match="overlap must be"):
            chunk_transcript("some text", chunk_size=10, overlap=10)

    def test_overlap_greater_than_chunk_size_raises(self):
        with pytest.raises(ValueError, match="overlap must be"):
            chunk_transcript("some text", chunk_size=10, overlap=15)


# ── chunking behaviour ─────────────────────────────────────────────────────────

class TestChunkingBehaviour:

    def test_chunk_count_is_correct(self):
        # 20 words, chunk_size=10, overlap=2 → step=8
        # chunk 1: words 0-9, chunk 2: words 8-17, chunk 3: words 16-19
        transcript = make_transcript(20)
        result = chunk_transcript(transcript, chunk_size=10, overlap=2)
        assert len(result) == 3

    def test_no_overlap_produces_sequential_chunks(self):
        words = [str(i) for i in range(10)]
        transcript = " ".join(words)
        result = chunk_transcript(transcript, chunk_size=5, overlap=0)
        assert result == ["0 1 2 3 4", "5 6 7 8 9"]

    def test_overlap_words_appear_in_consecutive_chunks(self):
        # overlap=2 means last 2 words of chunk N == first 2 words of chunk N+1
        words = [str(i) for i in range(10)]
        transcript = " ".join(words)
        result = chunk_transcript(transcript, chunk_size=5, overlap=2)

        chunk1_words = result[0].split()
        chunk2_words = result[1].split()
        # Last 2 words of chunk1 should be first 2 words of chunk2
        assert chunk1_words[-2:] == chunk2_words[:2]

    def test_all_words_are_covered(self):
        # Every word should appear in at least one chunk
        words = [str(i) for i in range(25)]
        transcript = " ".join(words)
        result = chunk_transcript(transcript, chunk_size=10, overlap=3)
        all_words_in_chunks = " ".join(result).split()
        for word in words:
            assert word in all_words_in_chunks

    def test_chunks_contain_no_leading_trailing_whitespace(self):
        transcript = make_transcript(50)
        result = chunk_transcript(transcript, chunk_size=10, overlap=2)
        for chunk in result:
            assert chunk == chunk.strip()

    def test_extra_whitespace_in_transcript_is_normalized(self):
        transcript = "word1   word2\t\tword3\nword4"
        result = chunk_transcript(transcript, chunk_size=10, overlap=0)
        assert result == ["word1 word2 word3 word4"]

    def test_last_chunk_contains_remaining_words(self):
        # 12 words, chunk_size=10, overlap=2 → step=8
        # chunk1: 0-9, chunk2: 8-11 (only 4 words)
        words = [str(i) for i in range(12)]
        transcript = " ".join(words)
        result = chunk_transcript(transcript, chunk_size=10, overlap=2)
        last_chunk_words = result[-1].split()
        assert "11" in last_chunk_words  # last word always in last chunk


# ── default parameters ─────────────────────────────────────────────────────────

class TestDefaults:

    def test_default_chunk_size_is_1000(self):
        transcript = make_transcript(1500)
        result = chunk_transcript(transcript)
        # First chunk should have exactly 1000 words
        assert len(result[0].split()) == 1000

    def test_default_overlap_is_150(self):
        transcript = make_transcript(1500)
        result = chunk_transcript(transcript)
        # Last 150 words of chunk 1 == first 150 words of chunk 2
        chunk1_words = result[0].split()
        chunk2_words = result[1].split()
        assert chunk1_words[-150:] == chunk2_words[:150]
