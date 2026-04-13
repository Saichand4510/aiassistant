# import whisper

# model = whisper.load_model("base")

# def transcribe_audio(file_path):
#     print(1111)
#     result = model.transcribe(file_path)
#     # return result["segments"]   # important: we need timestamps
#     print(result)
#     return result["text"]

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo",  # 🔥 use this
            response_format="json"
        )

    return response.text