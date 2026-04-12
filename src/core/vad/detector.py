"""VAD detection using ffmpeg silencedetect filter.

No PyTorch/Silero dependencies — just ffmpeg + Whisper API.
Extracted from working prototype at scripts/vad_whisper.py.
"""

import subprocess
import os
import tempfile
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def detect_speech_segments(
    audio_path: str,
    noise_db: int = -30,
    min_silence: float = 0.5,
    merge_gap: float = 2.0,
    min_segment: float = 0.3,
    chunk_size: int = 30,
) -> Tuple[List[Tuple[float, float]], float]:
    """
    Use ffmpeg silencedetect to find speech segments in an audio file.

    Args:
        audio_path: Path to audio file
        noise_db: Silence threshold in dB (default -30)
        min_silence: Minimum silence duration in seconds (default 0.5)
        merge_gap: Merge segments closer than this (seconds, default 2.0)
        min_segment: Skip segments shorter than this (seconds, default 0.3)
        chunk_size: Max chunk size in seconds (default 30)

    Returns:
        Tuple of (chunked_segments, total_duration)
        Each segment is (start_seconds, end_seconds)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    result = subprocess.run(
        [
            'ffmpeg', '-i', audio_path,
            '-af', f'silencedetect=noise={noise_db}dB:d={min_silence}',
            '-f', 'null', '-'
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    lines = result.stderr.split('\n')
    silence_starts = []
    silence_ends = []

    for line in lines:
        if 'silence_start:' in line:
            silence_starts.append(float(line.split('silence_start:')[1].strip()))
        elif 'silence_end:' in line:
            silence_ends.append(
                float(line.split('silence_end:')[1].split('|')[0].strip())
            )

    # Get total duration
    duration = 0.0
    for line in lines:
        if 'Duration:' in line:
            parts = line.split('Duration:')[1].split(',')[0].strip().split(':')
            duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break

    if duration == 0:
        logger.warning("Could not determine audio duration for %s", audio_path)
        return [], 0.0

    # Build speech segments (inverse of silence)
    segments = []
    current = 0.0

    for i, ss in enumerate(silence_starts):
        se = silence_ends[i] if i < len(silence_ends) else duration
        if ss > current + 0.1:  # At least 100ms of speech
            segments.append((current, ss))
        current = se

    if current < duration - 0.1:
        segments.append((current, duration))

    # Merge segments that are close together
    merged = []
    for seg in segments:
        if seg[1] - seg[0] < min_segment:
            continue
        if merged and seg[0] - merged[-1][1] < merge_gap:
            merged[-1] = (merged[-1][0], seg[1])
        else:
            merged.append(seg)

    # Chunk into ~chunk_size blocks for efficient API calls
    chunked = []
    for start, end in merged:
        segment_duration = end - start
        if segment_duration <= chunk_size:
            chunked.append((start, end))
            continue

        pos = start
        parent_chunks = []
        while pos < end:
            chunk_end = min(pos + chunk_size, end)
            parent_chunks.append((pos, chunk_end))
            pos = chunk_end

        # Avoid tiny leftover tail chunks — merge them back into the previous chunk.
        if len(parent_chunks) >= 2:
            last_start, last_end = parent_chunks[-1]
            if (last_end - last_start) < min_segment:
                prev_start, _ = parent_chunks[-2]
                parent_chunks[-2] = (prev_start, last_end)
                parent_chunks.pop()

        chunked.extend(parent_chunks)

    speech_time = sum(e - s for s, e in chunked)
    logger.info(
        "VAD: %s — %.0fs total, %.0fs speech, %d segments",
        os.path.basename(audio_path), duration, speech_time, len(chunked),
    )

    return chunked, duration


def extract_segment(
    audio_path: str,
    start: float,
    end: float,
    output_path: str,
    sample_rate: int = 16000,
) -> str:
    """
    Extract a segment of audio using ffmpeg.

    Args:
        audio_path: Source audio file
        start: Start time in seconds
        end: End time in seconds
        output_path: Where to write the extracted segment
        sample_rate: Output sample rate (default 16000)

    Returns:
        output_path
    """
    subprocess.run(
        [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-ss', str(start),
            '-to', str(end),
            '-acodec', 'aac',
            '-ar', str(sample_rate),
            '-ac', '1',
            output_path,
        ],
        capture_output=True,
        timeout=60,
    )
    return output_path
