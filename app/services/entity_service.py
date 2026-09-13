import re
from typing import Dict, Any

def _parse_time(time_str: str) -> str:
    """Best-effort time normalization to HH:MM."""
    time_str = time_str.lower().strip()
    
    # Simple regex for HH:MM am/pm or HH am/pm
    m = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_str)
    if m:
        h_str, m_str, ampm = m.groups()
        h = int(h_str)
        minute = int(m_str) if m_str else 0
        
        if ampm == "pm" and h < 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
            
        return f"{h:02d}:{minute:02d}"
    
    # Word-numbers fallback
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12
    }
    for word, num in word_to_num.items():
        if word in time_str:
            h = num
            if "pm" in time_str and h < 12:
                h += 12
            elif "am" in time_str and h == 12:
                h = 0
            return f"{h:02d}:00"
            
    return time_str

def extract_entities(text: str, intent: str) -> Dict[str, Any]:
    text_lower = text.lower()
    entities = {}
    missing_required_entities = []

    if intent == "set_alarm":
        # match time
        time_match = re.search(r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(?:o'clock|am|pm)?)\b", text_lower)
        if time_match:
            time_raw = time_match.group(1)
            entities["time"] = _parse_time(time_raw)
        else:
            entities["time"] = None
            missing_required_entities.append("time")
            
        # simple date extraction
        date_match = re.search(r"\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", text_lower)
        if date_match:
            entities["date"] = date_match.group(1)
            
    elif intent == "play_music":
        # Check for artist
        artist_match = re.search(r"play something by (.*)", text_lower)
        if artist_match:
            entities["artist"] = artist_match.group(1).strip()
        else:
            playlist_match = re.search(r"play (.*?) (?:songs|playlist)", text_lower)
            if playlist_match:
                entities["playlist"] = playlist_match.group(1).strip()
            else:
                song_match = re.search(r"play (.*)", text_lower)
                if song_match:
                    entities["song_name"] = song_match.group(1).strip()
                    
        if not entities:
            missing_required_entities.append("media")

    elif intent == "ask_weather":
        loc_match = re.search(r"in (\w+(?: \w+)*)", text_lower)
        if loc_match:
            entities["location"] = loc_match.group(1)
            
        time_match = re.search(r"\b(today|tomorrow|this weekend|tonight)\b", text_lower)
        if time_match:
            entities["time_reference"] = time_match.group(1)
            
    elif intent == "translate_text":
        lang_match = re.search(r"(?:to|in) ([a-z]+)$", text_lower)
        if lang_match:
            entities["target_language"] = lang_match.group(1)
        else:
            entities["target_language"] = None
            missing_required_entities.append("target_language")
            
        source_match = re.search(r"(?:translate|how do you say|what does) (.*?) (?:mean |to |in )", text_lower)
        if source_match:
            entities["source_text"] = source_match.group(1).strip()
        else:
            entities["source_text"] = None
            missing_required_entities.append("source_text")
            
    elif intent == "send_message":
        recipient = None
        msg_body = None
        
        tell_match = re.search(r"(?:tell|text) (\w+) (.*)", text_lower)
        if tell_match:
            recipient = tell_match.group(1)
            msg_body = tell_match.group(2)
        else:
            send_match = re.search(r"send(?: a message)? to (\w+) (?:saying |that )?(.*)", text_lower)
            if send_match:
                recipient = send_match.group(1)
                msg_body = send_match.group(2)
                
        if recipient:
            entities["recipient"] = recipient
        else:
            entities["recipient"] = None
            missing_required_entities.append("recipient")
            
        if msg_body:
            entities["message_body"] = msg_body
        else:
            entities["message_body"] = None
            missing_required_entities.append("message_body")
            
    elif intent in ["general_query", "unknown_intent"]:
        pass

    return {
        "entities": entities,
        "missing_required_entities": missing_required_entities
    }
