from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
load_dotenv()
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
   use_auth_token=os.getenv("HUGGINGFACE_TOKEN")
)

def get_speaker_segments(file_path):
    diarization = pipeline(file_path)

    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return speakers