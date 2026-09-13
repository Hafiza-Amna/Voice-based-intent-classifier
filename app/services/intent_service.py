'''Intent classification service using Groq.'''
import json
import re
from typing import Optional, Dict

import httpx
from groq import Groq

from app.config import settings

SYSTEM_PROMPT = """You are an intent classifier for a voice assistant. Classify the user's command into EXACTLY ONE of these intents:

- set_alarm: Command asks to create a time-based reminder/alarm (action verb like "set/wake me/remind" + a time).
- play_music: Command explicitly requests media playback (verb like "play/put on/start" + song/artist/playlist).
- ask_weather: Command asks for current/forecasted weather conditions (must include a weather-specific keyword: weather, rain, temperature, forecast, hot, cold, sunny).
- translate_text: Command asks to convert text/speech from one language to another (cue: translate/how do you say/what does X mean).
- send_message: Command asks to deliver a message/text to a named recipient (verb like "send/text/tell" + a named recipient).
- general_query: Anything else that doesn't clearly match the above (catch-all).

Respond with ONLY a JSON object, no other text, in this exact format:
{"intent": "<one of the 6 intents above>", "confidence": <float between 0 and 1>}

The confidence should reflect how certain you are. If the command is vague, ambiguous, or doesn't clearly fit any intent, still pick the closest one but give it a LOW confidence score (below 0.6)."""


def _extract_json(text: str) -> Optional[Dict]:
    """Extract a JSON object from a possibly fenced string."""
    cleaned = re.sub(r"^```json\s*|```\s*$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def classify_intent(text: str) -> dict:
    """Classify a user command using Groq's Llama 3.1 8B Instant model.

    Returns a dict with keys: intent (str), confidence (float), optional message (str).
    """
    client = Groq(api_key=settings.GROQ_API_KEY, timeout=10.0)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.0,
            max_tokens=256,
        )
        raw = response.choices[0].message.content
        parsed = _extract_json(raw)
        if not parsed:
            raise ValueError("Unable to parse JSON from model response")
        intent = parsed.get("intent", "unknown_intent")
        confidence = float(parsed.get("confidence", 0.0))
        threshold = getattr(settings, "confidence_threshold", 0.6)
        if confidence < threshold:
            return {
                "intent": "unknown_intent",
                "confidence": confidence,
                "message": "Command not confidently understood, please rephrase.",
            }
        return {"intent": intent, "confidence": confidence}
    except (httpx.RequestError, httpx.HTTPStatusError, TimeoutError):
        return {"intent": "unknown_intent", "confidence": 0.0, "message": "Classification service temporarily unavailable."}
    except Exception:
        return {"intent": "unknown_intent", "confidence": 0.0, "message": "Classification service temporarily unavailable."}
