import whisper

model = whisper.load_model("base")

def transcribe_audio(file_path):
    print(1111)
    result = model.transcribe(file_path)
    # return result["segments"]   # important: we need timestamps
    print(result)
    return result["text"]