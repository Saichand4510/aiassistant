from fastapi import FastAPI, UploadFile, File
import shutil
import os

from services.transcription import transcribe_audio
from services.diarization import get_speaker_segments
from services.merge import assign_speakers
from services.llm import extract_insights
import os
from db import SessionLocal,engine
from models import Meeting, ActionItem,Base,Decision,Question,Topic
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


from fastapi import UploadFile, File
import shutil
import os

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    db = SessionLocal()

    try:
        # -----------------------------
        # 1. Save uploaded file
        # -----------------------------
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -----------------------------
        # 2. Transcription + Diarization
        # -----------------------------
        transcript_segments = transcribe_audio(file_path)
        speaker_segments = get_speaker_segments(file_path)
        merged = assign_speakers(transcript_segments, speaker_segments)

        full_text = "\n".join(
            [f"{m['speaker']}: {m['text']}" for m in merged]
        )

        # -----------------------------
        # 3. LLM Insights
        # -----------------------------
        insights = extract_insights(full_text)

        # ❗ Handle LLM failure
        if "raw_output" in insights:
            return {"error": "LLM failed", "details": insights["raw_output"]}

        # -----------------------------
        # 4. Save Meeting
        # -----------------------------
        meeting = Meeting(
            file_name=file.filename,
            transcript=full_text,
            summary=str(insights.get("summary", ""))
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        # -----------------------------
        # 5. Save Action Items
        # -----------------------------
        for item in insights.get("action_items", []):
            db.add(ActionItem(
                meeting_id=meeting.id,
                task=item.get("task"),
                assignee=item.get("assignee"),
                deadline=item.get("deadline"),
                status="pending"
            ))

        # -----------------------------
        # 6. Save Decisions
        # -----------------------------
        for d in insights.get("decisions", []):
            db.add(Decision(
                meeting_id=meeting.id,
                decision_text=d
            ))

        # -----------------------------
        # 7. Save Questions
        # -----------------------------
        for q in insights.get("questions", []):
            db.add(Question(
                meeting_id=meeting.id,
                question_text=q
            ))

        # -----------------------------
        # 8. Save Topics
        # -----------------------------
        for t in insights.get("topics", []):
            db.add(Topic(
                meeting_id=meeting.id,
                topic_text=t
            ))

        # Final commit
        db.commit()

        # -----------------------------
        # 9. Response
        # -----------------------------
        return {
            "meeting_id": meeting.id,
            "summary": insights.get("summary", ""),
            "action_items": insights.get("action_items", []),
            "decisions": insights.get("decisions", []),
            "questions": insights.get("questions", []),
            "topics": insights.get("topics", [])
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()