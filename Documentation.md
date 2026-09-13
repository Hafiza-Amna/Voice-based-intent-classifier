# Voice-Based Intent Classifier — Technical Documentation

## 1. Finalized Intent Set

| Intent | Description | Required Entities | Optional Entities |
|---|---|---|---|
| `set_alarm` | Create a time-based reminder/alarm | time | date, label/note |
| `play_music` | Request media playback | at least one of: song_name, artist, playlist | — |
| `ask_weather` | Ask for current/forecasted weather | — (defaults to saved location) | location, date/time_reference |
| `translate_text` | Convert text/speech between languages | source_text, target_language | — |
| `send_message` | Deliver a message to a named recipient | recipient, message_body | — |
| `general_query` | Catch-all for anything else | — | — |
| `unknown_intent` | Fallback when confidence < 0.6 | — | — |

## 2. Intent Boundary Rules (Disambiguation)

- **set_alarm vs. ask_weather:** `set_alarm` always includes an action verb (set/wake me/remind) plus a time; `ask_weather` never includes an alarm/reminder verb.
- **play_music vs. general_query:** `play_music` always includes a playback verb (play/put on/start); music-related questions with no playback verb fall to `general_query`.
- **ask_weather vs. general_query:** `ask_weather` requires a weather-specific keyword (weather, rain, temperature, forecast, hot, cold, sunny).
- **translate_text vs. send_message:** `translate_text` requires a translation cue (translate/how do you say/what does X mean); if the primary action is delivering a message to a person, it is `send_message` even if a language is mentioned.
- **send_message:** requires both a communication verb (send/text/tell) AND a named recipient.

## 3. Confidence Threshold and Fallback Behavior

- Threshold: **0.6** (configurable via `CONFIDENCE_THRESHOLD` in `.env`).
- Below threshold -> `intent: "unknown_intent"`, empty `entities`, and a `message` field explaining the command was not understood confidently.
- At or above threshold -> normal intent, confidence, and entities are returned.

## 4. Missing / Unclear Entity Handling

- If a required entity is missing, the response still includes the predicted intent and confidence, plus a `missing_required_entities` list naming the missing field(s).
- If an entity value is ambiguous (e.g., "later" instead of a specific time), the raw phrase is kept as-is rather than guessed.
- Missing/unclear entities never block the API response.

## 5. Dataset Composition

- **Total:** 254 labeled examples.
- **Per intent:** ~33-35 positive examples plus hard-negative examples (look-alike commands correctly labeled with their true intent) and ambiguous examples (labeled `unknown_intent`).
- **Split:** 80% train (203 rows) / 20% test (51 rows), stratified by intent label via `scripts/split_dataset.py` (uses `sklearn.model_selection.train_test_split` with a fixed random seed for reproducibility).
- **Data quality rules applied:** no duplicate utterances, balanced class distribution, manually reviewed labels, natural (non-robotic) phrasing, no offensive content.

## 6. Evaluation Methodology and Results

- **Script:** `scripts/evaluate.py` loads `data/test_set.csv`, runs each example through the live `classify_intent()` function, and compares predictions against ground-truth labels.
- **Metrics:** overall accuracy, per-intent precision/recall/F1, and a full confusion matrix.
- **Target:** >=85% overall accuracy.
- **Result:** **92% overall accuracy - PASS.**
- **Per-intent results (representative run):** `play_music` and `translate_text` achieved perfect precision/recall; most confusion occurred between `send_message` and `unknown_intent`, and between `ask_weather`/`set_alarm` and `general_query` on a small number of edge cases - consistent with the intentionally difficult hard-negative examples included in the test set.

## 7. API Contract Reference

### POST /api/v1/classify-audio
Request: multipart/form-data, field audio_file.
Response example:
  transcription: "set an alarm for 7 am"
  intent: "set_alarm"
  confidence: 0.91
  entities: { time: "07:00" }
  processing_time: 1.4

### POST /api/v1/classify-text
Request: {"text": "play some coke studio songs"}
Response example:
  intent: "play_music"
  confidence: 0.88
  entities: { playlist: "coke studio" }

### GET /api/v1/health
Response: {"status": "healthy", "app_name": "voice-intent-classifier", "version": "1.0"}

## 8. Design Decisions Log

| Decision | Choice | Reason |
|---|---|---|
| Intent classification approach | LLM zero-shot (Groq) | No custom labeled training data required for MVP; fast to build and iterate |
| Entity extraction approach | Rule-based/regex | Simple, deterministic, no extra API cost per request |
| Confidence threshold | 0.6 | Balances rejecting ambiguous commands vs. over-rejecting valid ones |
| Train/test split | 80/20 stratified | Keeps per-intent balance while reserving a meaningful held-out test set |
| STT engine | faster-whisper (CPU, int8) | Fast, no GPU required, good accuracy/speed trade-off for MVP |

## 9. Known Issues / Non-Determinism

- LLM-based classification is not perfectly deterministic - running the evaluation script multiple times can produce slightly different accuracy figures (observed range: 90-92%) even with temperature=0.0, due to inherent model sampling behavior.
- Entity extraction is regex-based and may occasionally include extra words (e.g., capturing "some coke studio" instead of just "coke studio" for a playlist name) - acceptable for MVP, flagged as a future refinement.

## 10. Maintenance Notes

- To add a new intent: update the system prompt in `intent_service.py`, add extraction logic in `entity_service.py`, add labeled examples to `data/intents_dataset.csv`, and re-run `scripts/split_dataset.py` and `scripts/evaluate.py`.
- The Groq API key must be kept in `.env` (gitignored) and never committed or shared.
