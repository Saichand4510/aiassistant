from fastapi import FastAPI, UploadFile, File
import shutil
import os

from services.transcription import transcribe_audio
from services.diarization import get_speaker_segments
from services.merge import assign_speakers
from services.llm import extract_insights
import os
from db import SessionLocal,engine
from models import Meeting, ActionItem,Base
app = FastAPI()
Base.metadata.create_all(bind=engine)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# Upload Audio
# -------------------------
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "File uploaded", "path": file_path}


# -------------------------
# Join Meeting (Mock)
# -------------------------
@app.post("/join-meeting")
async def join_meeting(link: str):
    return {
        "message": f"Joining meeting at {link}",
        "status": "Recording started (simulated)"
    }


# -------------------------
# FULL ANALYSIS PIPELINE
# -------------------------


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    db = SessionLocal()

    # Save file
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process
    transcript_segments = transcribe_audio(file_path)
    speaker_segments = get_speaker_segments(file_path)
    merged = assign_speakers(transcript_segments, speaker_segments)

    full_text = "\n".join(
        [f"{m['speaker']}: {m['text']}" for m in merged]
    )

    insights = extract_insights(full_text)

    # Save meeting
    meeting = Meeting(
        file_name=file.filename,
        transcript=full_text,
        summary=str(insights)
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Save action items (assuming JSON output)
    for item in insights.get("action_items", []):
        action = ActionItem(
            meeting_id=meeting.id,
            task=item.get("task"),
            assignee=item.get("assignee"),
            deadline=item.get("deadline")
        )
        db.add(action)

    db.commit()

    return {
        "meeting_id": meeting.id,
        "insights": insights
    }