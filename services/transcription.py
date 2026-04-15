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
    # print("response",response.text)
    return response.text

import io
import io
import wave

def pcm_to_wav_bytes(pcm_bytes):
    buffer = io.BytesIO()

    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(16000)
        wf.writeframes(pcm_bytes)

    buffer.seek(0)
    return buffer
def transcribe_audio_bytes(audio_bytes):
    wav_file = pcm_to_wav_bytes(audio_bytes)  # ✅ convert first

    response = client.audio.transcriptions.create(
        file=("audio.wav", wav_file),
        model="whisper-large-v3-turbo",
        language='en'
    )

    return response.text