from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CV Job Category Predictor"
    APP_VERSION: str = "1.0.0"

    # Path ke file model dan encoder — sesuaikan dengan lokasi file Anda
    MODEL_PATH: str = "model/model.keras"
    ENCODER_PATH: str = "model/label_encoder.pkl"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
