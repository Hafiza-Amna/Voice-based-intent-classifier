import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def display_result(result: dict):
    intent = result.get("intent")
    confidence = result.get("confidence", 0)
    message = result.get("message")
    transcription = result.get("transcription")
    entities = result.get("entities", {})
    missing_entities = result.get("missing_required_entities", [])

    if intent == "unknown_intent":
        st.warning(message or "Command not confidently understood, please rephrase.")
    else:
        st.success(f"**{intent}** ({confidence * 100:.0f}% confident)")
    
    if transcription:
        st.info(f"**Transcription:** {transcription}")
        
    if entities:
        st.write("Extracted Entities:")
        st.json(entities)
        
    if missing_entities:
        st.warning(f"Missing: {', '.join(missing_entities)} — please specify.")


st.title("🎙️ Voice-Based Intent Classifier")
st.write("Upload an audio command or type a text command to classify its intent.")

# Sidebar Health Check
try:
    health_resp = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
    if health_resp.status_code == 200:
        st.sidebar.success("🟢 Backend Connected")
    else:
        st.sidebar.error("🔴 Backend Unreachable")
except requests.exceptions.RequestException:
    st.sidebar.error("🔴 Backend Unreachable")

def classify_audio_file(file_bytes, filename, content_type):
    with st.spinner("Classifying audio..."):
        try:
            files = {"audio_file": (filename, file_bytes, content_type)}
            resp = requests.post(f"{BACKEND_URL}/api/v1/classify-audio", files=files, timeout=30)
            if resp.status_code == 200:
                display_result(resp.json())
            else:
                st.error(f"Error: {resp.status_code} - {resp.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Backend unreachable or request failed: {e}")

tab1, tab2, tab3 = st.tabs(["🎤 Record Voice", "📁 Upload Audio", "⌨️ Type Text"])

with tab1:
    audio_value = st.audio_input("Record your command")
    st.caption("Click the mic, speak your command, then click Classify.")
    if audio_value is not None:
        st.audio(audio_value)
        if st.button("Classify", key="record_btn"):
            classify_audio_file(audio_value.getvalue(), "recorded_audio.wav", "audio/wav")

with tab2:
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a", "ogg"])
    if uploaded_file is not None:
        if st.button("Classify", key="audio_btn"):
            classify_audio_file(uploaded_file.getvalue(), uploaded_file.name, uploaded_file.type)

with tab3:
    text_input = st.text_input("Type a command:")
    if st.button("Classify", key="text_btn") and text_input:
        with st.spinner("Classifying text..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/api/v1/classify-text", json={"text": text_input}, timeout=10)
                if resp.status_code == 200:
                    display_result(resp.json())
                else:
                    st.error(f"Error: {resp.status_code} - {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Backend unreachable or request failed: {e}")
