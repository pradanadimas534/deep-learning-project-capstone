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


class PredictionResponse(BaseModel):
    """Response hasil prediksi."""

    kategori: str = Field(..., description="Kategori pekerjaan hasil prediksi.")
    confidence: float = Field(..., description="Confidence score dalam persen (0–100).")
    status: str = Field(default="success", description="Status prediksi.")


class ErrorResponse(BaseModel):
    """Response saat terjadi error."""

    status: str = Field(default="error")
    detail: str
