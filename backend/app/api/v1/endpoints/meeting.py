import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.agents import MeetingSummaryRequest, MeetingSummaryResponse
from app.services.agents.meeting_agent import summarize_meeting
from app.services.transcription.transcriber import transcribe_meeting_file

router = APIRouter()


@router.post("/meeting/summarize", response_model=MeetingSummaryResponse)
async def summarize(request: MeetingSummaryRequest) -> MeetingSummaryResponse:
    """Summarize a meeting when you already have a text transcript."""
    summary = await summarize_meeting(request.transcript)
    return MeetingSummaryResponse(summary=summary)


@router.post("/meeting/summarize-from-recording", response_model=MeetingSummaryResponse)
async def summarize_from_recording(file: UploadFile = File(...)) -> MeetingSummaryResponse:
    """
    Upload a Zoom/Teams/Meet recording (audio or video) directly.
    Pipeline: extract audio -> transcribe (Groq Whisper) -> summarize.
    """
    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transcript = await transcribe_meeting_file(tmp_path)
        summary = await summarize_meeting(transcript)
        return MeetingSummaryResponse(summary=summary, transcript=transcript)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to process recording: {exc}") from exc
    finally:
        os.remove(tmp_path)

