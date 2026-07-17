"""
Turns a meeting recording (audio or video) into text.

Pipeline: video -> (ffmpeg) -> audio -> (Groq Whisper) -> transcript text

Groq's Whisper endpoint is free-tier and uses the same GROQ_API_KEY you
already have — no extra signup needed.
"""
import os
import subprocess
import uuid

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


def extract_audio_if_video(file_path: str) -> str:
    """
    If file_path is a video, extract its audio track to a temp .mp3 and
    return that path. If it's already audio, return file_path unchanged.
    Requires ffmpeg to be installed and on PATH.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in AUDIO_EXTENSIONS:
        return file_path

    if ext not in VIDEO_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{ext}'. Use a video or audio file.")

    audio_path = os.path.join(
        os.path.dirname(file_path), f"{uuid.uuid4().hex}.mp3"
    )
    logger.info(f"Extracting audio from video: {file_path} -> {audio_path}")

    result = subprocess.run(
        ["ffmpeg", "-y", "-i", file_path, "-vn", "-acodec", "libmp3lame", audio_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed to extract audio. Is ffmpeg installed and on PATH? "
            f"stderr: {result.stderr[-500:]}"
        )
    return audio_path


async def transcribe_audio(audio_path: str) -> str:
    """Send an audio file to Groq's Whisper endpoint and return plain text."""
    client = AsyncGroq(api_key=settings.groq_api_key)

    with open(audio_path, "rb") as f:
        transcription = await client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    # SDK returns either a plain string or an object with .text depending on version
    return transcription if isinstance(transcription, str) else transcription.text


async def transcribe_meeting_file(file_path: str) -> str:
    """Full pipeline: video-or-audio file in -> transcript text out."""
    audio_path = extract_audio_if_video(file_path)
    transcript = await transcribe_audio(audio_path)

    if audio_path != file_path:
        os.remove(audio_path)  # clean up the extracted temp audio

    return transcript
