def assign_speakers(transcript_segments, speaker_segments):
    final_output = []

    for segment in transcript_segments:
        seg_start = segment["start"]
        seg_end = segment["end"]
        text = segment["text"]

        speaker_label = "Unknown"

        for sp in speaker_segments:
            if seg_start >= sp["start"] and seg_end <= sp["end"]:
                speaker_label = sp["speaker"]
                break

        final_output.append({
            "speaker": speaker_label,
            "text": text
        })

    return final_output