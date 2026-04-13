from fastapi import FastAPI, UploadFile, File
import shutil
import os

from services.transcription import transcribe_audio
# from services.diarization import get_speaker_segments
# from services.merge import assign_speakers
from services.llm import extract_insights
import os
from db import SessionLocal,engine
from models import Meeting, ActionItem,Base,Decision,Question,Topic
app = FastAPI()
Base.metadata.create_all(bind=engine)
DATA_DIR = "data"
# os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# Upload Audio
# -------------------------
@app.post("/meetings")
def create_meeting(title: str, date: str, participants: str, meeting_link: str = None):
    db = SessionLocal()

    meeting = Meeting(
        title=title,
        date=date,
        participants=participants,
        meeting_link=meeting_link
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    db.close()

    return {"meeting_id": meeting.id}


# -------------------------
# Join Meeting (Mock)
# -------------------------


# -------------------------
# FULL ANALYSIS PIPELINE
# -------------------------
@app.post("/analyze/{meeting_id}")
async def analyze(meeting_id: int, file: UploadFile = File(...)):

    db = SessionLocal()

    try:
        file_path = f"{DATA_DIR}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # transcription
        transcript = transcribe_audio(file_path)

        # LLM insights
        insights = extract_insights(transcript)

        if "raw_output" in insights:
            return {"error": "LLM failed", "details": insights["raw_output"]}

        # update meeting
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

        meeting.file_name = file.filename
        meeting.transcript = transcript
        meeting.summary = insights.get("summary", "")

        db.commit()

        # save action items
        for item in insights.get("action_items", []):
            db.add(ActionItem(
                meeting_id=meeting_id,
                task=item.get("task"),
                assignee=item.get("assignee"),
                deadline=item.get("deadline"),
                status="pending"
            ))

        # save decisions
        for d in insights.get("decisions", []):
            db.add(Decision(meeting_id=meeting_id, decision_text=d))

        # save questions
        for q in insights.get("questions", []):
            db.add(Question(meeting_id=meeting_id, question_text=q))

        # save topics
        for t in insights.get("topics", []):
            db.add(Topic(meeting_id=meeting_id, topic_text=t))

        db.commit()

        return {
            "meeting_id": meeting_id,
            "summary": insights.get("summary"),
            "action_items": insights.get("action_items")
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()



# @app.post("/analyze")
# async def analyze(file: UploadFile = File(...)):

#     db = SessionLocal()

#     try:
#         # -----------------------------
#         # 1. Save uploaded file
#         # -----------------------------
#         BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#         DATA_DIR = os.path.join(BASE_DIR, "data")

#         os.makedirs(DATA_DIR, exist_ok=True)
#         file_path =os.path.join(DATA_DIR, file.filename)
        

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # -----------------------------
#         # 2. Transcription + Diarization
#         # -----------------------------
#         # transcript_segments = transcribe_audio(file_path)
#         # speaker_segments = get_speaker_segments(file_path)
#         # merged = assign_speakers(transcript_segments, speaker_segments)

#         # full_text = "\n".join(
#         #     [f"{m['speaker']}: {m['text']}" for m in merged]
#         # )
#         print("Saved at:", file_path)
#         full_text = transcribe_audio(file_path)

#         print("Saved at:", file_path)
#         # -----------------------------
#         # 3. LLM Insights
#         # -----------------------------
#         insights = extract_insights(full_text)

#         # ❗ Handle LLM failure
#         if "raw_output" in insights:
#             return {"error": "LLM failed", "details": insights["raw_output"]}

#         # -----------------------------
#         # 4. Save Meeting
#         # -----------------------------
#         meeting = Meeting(
#             file_name=file.filename,
#             transcript=full_text,
#             summary=str(insights.get("summary", ""))
#         )
#         db.add(meeting)
#         db.commit()
#         db.refresh(meeting)

#         # -----------------------------
#         # 5. Save Action Items
#         # -----------------------------
#         for item in insights.get("action_items", []):
#             db.add(ActionItem(
#                 meeting_id=meeting.id,
#                 task=item.get("task"),
#                 assignee=item.get("assignee"),
#                 deadline=item.get("deadline"),
#                 status="pending"
#             ))

#         # -----------------------------
#         # 6. Save Decisions
#         # -----------------------------
#         for d in insights.get("decisions", []):
#             db.add(Decision(
#                 meeting_id=meeting.id,
#                 decision_text=d
#             ))

#         # -----------------------------
#         # 7. Save Questions
#         # -----------------------------
#         for q in insights.get("questions", []):
#             db.add(Question(
#                 meeting_id=meeting.id,
#                 question_text=q
#             ))

#         # -----------------------------
#         # 8. Save Topics
#         # -----------------------------
#         for t in insights.get("topics", []):
#             db.add(Topic(
#                 meeting_id=meeting.id,
#                 topic_text=t
#             ))

#         # Final commit
#         db.commit()

#         # -----------------------------
#         # 9. Response
#         # -----------------------------
#         return {
#             "meeting_id": meeting.id,
#             "summary": insights.get("summary", ""),
#             "action_items": insights.get("action_items", []),
#             "decisions": insights.get("decisions", []),
#             "questions": insights.get("questions", []),
#             "topics": insights.get("topics", [])
#         }

#     except Exception as e:
#         db.rollback()
#         return {"error": str(e)}

#     finally:
#         db.close()

@app.get("/meetings")
def get_meetings():
    db = SessionLocal()

    meetings = db.query(Meeting).all()

    result = [
        {
            "id": m.id,
            "title": m.title,
            "date": m.date
        }
        for m in meetings
    ]

    db.close()
    return result 

@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    db = SessionLocal()

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    actions = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()
    decisions = db.query(Decision).filter(Decision.meeting_id == meeting_id).all()
    questions = db.query(Question).filter(Question.meeting_id == meeting_id).all()
    topics = db.query(Topic).filter(Topic.meeting_id == meeting_id).all()

    db.close()

    return {
        "meeting": meeting.summary,
        "action_items": actions,
        "decisions": decisions,
        "questions": questions,
        "topics": topics
    }


@app.get("/action-items")
def get_action_items():
    db = SessionLocal()

    items = db.query(ActionItem).all()

    db.close()
    return items 

@app.put("/action-items/{item_id}")
def update_action(item_id: int, status: str):
    db = SessionLocal()

    item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    item.status = status

    db.commit()
    db.close()

    return {"message": "updated"}
