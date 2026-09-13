import time
from app.services.stt_service import transcribe_audio, STTServiceError
from app.services.intent_service import classify_intent
from app.services.entity_service import extract_entities

def process_audio_command(file_path: str) -> dict:
    start_time = time.time()
    
    # STT
    transcription = transcribe_audio(file_path)
    
    # Intent Classification
    intent_result = classify_intent(transcription)
    intent = intent_result.get("intent", "unknown_intent")
    confidence = intent_result.get("confidence", 0.0)
    message = intent_result.get("message")
    
    # Entity Extraction
    if intent == "unknown_intent":
        entities = {}
        missing_entities = []
    else:
        entity_result = extract_entities(transcription, intent)
        entities = entity_result.get("entities", {})
        missing_entities = entity_result.get("missing_required_entities", [])
        
    end_time = time.time()
    
    return {
        "transcription": transcription,
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "message": message,
        "missing_required_entities": missing_entities,
        "processing_time": end_time - start_time
    }

def process_text_command(text: str) -> dict:
    start_time = time.time()
    
    # Intent Classification
    intent_result = classify_intent(text)
    intent = intent_result.get("intent", "unknown_intent")
    confidence = intent_result.get("confidence", 0.0)
    message = intent_result.get("message")
    
    # Entity Extraction
    if intent == "unknown_intent":
        entities = {}
        missing_entities = []
    else:
        entity_result = extract_entities(text, intent)
        entities = entity_result.get("entities", {})
        missing_entities = entity_result.get("missing_required_entities", [])
        
    end_time = time.time()
    
    return {
        "transcription": text,
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "message": message,
        "missing_required_entities": missing_entities,
        "processing_time": end_time - start_time
    }
