from typing import List, Optional
from pydantic import BaseModel, Field


class CVTextRequest(BaseModel):
    teks_cv: str = Field(
        ...,
        min_length=10,
        description="Isi teks CV yang akan dianalisis.",
        examples=[
            "Nama: Budi. Pengalaman 3 tahun sebagai software engineer. "
            "Menguasai Python, React, Docker, AWS, SQL."
        ],
    )


class RekomendasiItem(BaseModel):
    job_title:         str            = Field(..., description="Nama posisi pekerjaan.")
    company:           str            = Field(..., description="Nama perusahaan.")
    location:          str            = Field(..., description="Lokasi pekerjaan.")
    salary:            Optional[float]= Field(None, description="Gaji (jika tersedia).")
    skills_dibutuhkan: List[str]      = Field(..., description="Skill yang dibutuhkan perusahaan untuk posisi ini.")
    match:             int            = Field(..., description="Persentase kesesuaian skill CV vs skill dibutuhkan (0-100).")


class PredictionResponse(BaseModel):
    kategori:    str                  = Field(..., description="Kategori hasil prediksi model.")
    confidence:  float                = Field(..., description="Confidence score model dalam persen.")
    is_valid:    bool                 = Field(..., description="True jika prediksi valid dan skill terdeteksi.")
    pesan:       Optional[str]        = Field(None, description="Pesan jika prediksi tidak valid.")
    skills:      List[str]            = Field(default=[], description="Skill yang terdeteksi dari CV.")
    rekomendasi: List[RekomendasiItem]= Field(default=[], description="Lowongan yang paling cocok dengan skill CV.")
    gap_skills:  List[str]            = Field(default=[], description="Skill yang belum dimiliki tapi dibutuhkan.")
    status:      str                  = Field(default="success")


class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    detail: str