from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from app.config import settings
from app.models.schemas import HealthResponse, ClassificationResponse, ClassifyTextRequest
from app.core.orchestrator import process_audio_command, process_text_command
from app.services.stt_service import STTServiceError

api_router = APIRouter()

@api_router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "app_name": getattr(settings, "app_name", "App"),
        "version": getattr(settings, "app_version", "1.0.0")
    }

@api_router.post("/classify-text", response_model=ClassificationResponse)
def classify_text(request: ClassifyTextRequest):
    result = process_text_command(request.text)
    return result

@api_router.post("/classify-audio", response_model=ClassificationResponse)
def classify_audio(audio_file: UploadFile = File(...)):
    # Validate extension
    ext = os.path.splitext(audio_file.filename)[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".ogg"]:
        raise HTTPException(status_code=400, detail=f"Invalid file extension: {ext}. Allowed: .wav, .mp3, .m4a, .ogg")
        
    # Read content to check size and save
    content = audio_file.file.read()
    
    max_size_mb = getattr(settings, "max_audio_file_size_mb", 5)
    if len(content) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {max_size_mb} MB")
        
    # Save to temp file
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, 'wb') as f:
        f.write(content)
        
    try:
        result = process_audio_command(temp_path)
        return result
    except STTServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

