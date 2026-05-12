from typing import List
from pydantic import BaseModel, Field


class CVTextRequest(BaseModel):
    """Body request untuk prediksi dari teks CV."""

    teks_cv: str = Field(
        ...,
        min_length=10,
        description="Isi teks CV yang akan diprediksi kategori pekerjaannya.",
        examples=[
            "Nama: Budi Santoso. Pengalaman: 3 tahun sebagai Data Analyst di perusahaan fintech. "
            "Keahlian: Python, SQL, Tableau, Machine Learning."
        ],
    )


class RekomendasiRole(BaseModel):
    """Satu item rekomendasi role pekerjaan."""
    role: str = Field(..., description="Nama role pekerjaan.")
    match: int = Field(..., description="Persentase kesesuaian role (0–100).")


class PredictionResponse(BaseModel):
    """Response lengkap hasil prediksi CV."""

    kategori: str = Field(..., description="Kategori pekerjaan hasil prediksi model.")
    confidence: float = Field(..., description="Confidence score prediksi dalam persen (0–100).")
    skills: List[str] = Field(default=[], description="Daftar skill yang terdeteksi dari teks CV.")
    rekomendasi: List[RekomendasiRole] = Field(default=[], description="Daftar rekomendasi role beserta persentase match.")
    gap_skills: List[str] = Field(default=[], description="Skill yang belum dimiliki tapi dibutuhkan untuk kategori ini.")
    status: str = Field(default="success", description="Status prediksi.")


class ErrorResponse(BaseModel):
    """Response saat terjadi error."""
    status: str = Field(default="error")
    detail: str
