from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ClassifyTextRequest(BaseModel):
    text: str

class ClassificationResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict
    transcription: Optional[str] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None
    missing_required_entities: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
