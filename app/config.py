import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "voice-intent-classifier"
    app_version: str = "1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    max_audio_file_size_mb: int = 10
    confidence_threshold: float = 0.6
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
