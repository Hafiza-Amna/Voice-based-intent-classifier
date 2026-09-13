from faster_whisper import WhisperModel
import os

class STTServiceError(Exception):
    pass

# Load model once at module level
try:
    _model = WhisperModel("base", device="cpu", compute_type="int8")
except Exception as e:
    _model = None
    print(f"Warning: Failed to pre-load Whisper model: {e}")

def transcribe_audio(file_path: str) -> str:
    global _model
    
    try:
        if _model is None:
            _model = WhisperModel("base", device="cpu", compute_type="int8")
            
        segments, info = _model.transcribe(file_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text.strip().lower()
    except Exception as e:
        raise STTServiceError(f"Failed to transcribe audio: {e}")
