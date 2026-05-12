from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "CV Job Category Predictor"
    APP_VERSION: str = "1.0.0"

    # Path ke file model dan encoder
    MODEL_PATH: str = "model/model.keras"
    ENCODER_PATH: str = "model/label_encoder.pkl"

    # CORS — pisahkan beberapa origin dengan koma di .env
    # Contoh: ALLOWED_ORIGINS="http://localhost:3000,http://192.168.1.10:3000"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",       # Next.js dev lokal
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parsing string dari .env jadi list, misal: 'http://a.com,http://b.com'"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
