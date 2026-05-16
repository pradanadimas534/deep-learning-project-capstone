from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "CV Job Category Predictor"
    APP_VERSION: str = "1.0.0"

    MODEL_PATH:   str = "model/model.keras"
    ENCODER_PATH: str = "model/label_encoder.pkl"

    # Dataset CSV — sumber data lowongan asli
    DATASET_PATH: str = "data/all_jobs_data.csv"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()