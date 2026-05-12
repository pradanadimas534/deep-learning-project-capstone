from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "CV Job Category Predictor"
    APP_VERSION: str = "1.0.0"

    MODEL_PATH: str = "model/model.keras"
    ENCODER_PATH: str = "model/encoder.pkl"

    # Dibangun dari dataset CSV via build_skill_reference.py
    SKILL_REFERENCE_PATH: str = "model/skill_reference.json"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
