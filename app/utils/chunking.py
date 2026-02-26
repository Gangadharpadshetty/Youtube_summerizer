"""Transcript chunking utilities.

This module provides a deterministic, whitespace-safe chunking function
that splits transcripts into approximately `chunk_size` tokens (words)
with a fixed word overlap between chunks.

Notes:
- Uses words (whitespace-separated) as token approximation to avoid
  introducing external tokenizer dependencies.
- Deterministic: same input produces same chunks.
"""
from typing import List
import re


def chunk_transcript(transcript: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Split `transcript` into chunks of about `chunk_size` tokens with `overlap` tokens overlap.

    - transcript: raw transcript string
    - chunk_size: desired number of tokens (words) per chunk
    - overlap: number of tokens to overlap between consecutive chunks

    Returns a list of chunk strings.
    """
    if not transcript:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >=0 and < chunk_size")

    # Normalize whitespace and split into words (deterministic)
    words = re.findall(r"\S+", transcript)
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    n = len(words)

    while start < n:
        end = start + chunk_size
        chunk_words = words[start:end]
        # Join with single space to clean extra whitespace
        chunk_text = " ".join(chunk_words).strip()
        if chunk_text:
            chunks.append(chunk_text)

        # Advance start by chunk_size - overlap to create desired overlap
        if end >= n:
            break
        start = end - overlap

    return chunks
