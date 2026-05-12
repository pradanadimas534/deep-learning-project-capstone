from fastapi import APIRouter, HTTPException, status

from app.schemas.cv_schema import CVTextRequest, PredictionResponse, RekomendasiRole
from app.services.cv_prediction_service import CVPredictionService
from app.services.cv_analyzer_service import CVAnalyzerService

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Prediksi kategori + analisis lengkap CV",
    description=(
        "Menerima teks CV dan mengembalikan prediksi kategori, "
        "skill yang terdeteksi, rekomendasi role, dan gap skills."
    ),
    tags=["Prediction"],
)
def predict_cv(payload: CVTextRequest) -> PredictionResponse:
    """
    **Request body:**
    - `teks_cv` – Isi teks CV (minimal 10 karakter).

    **Response:**
    - `kategori`    – Kategori pekerjaan hasil prediksi model.
    - `confidence`  – Confidence score model dalam persen (0–100).
    - `skills`      – Skill yang terdeteksi dari teks CV.
    - `rekomendasi` – Daftar role yang cocok beserta match percentage.
    - `gap_skills`  – Skill yang belum dimiliki tapi dibutuhkan.
    - `status`      – `"success"` jika berhasil.
    """
    # Step 1 — Prediksi kategori dari model TF
    try:
        kategori, confidence = CVPredictionService.predict(payload.teks_cv)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat prediksi: {str(e)}",
        )

    # Step 2 — Analisis skills, rekomendasi, gap skills
    try:
        skills, rekomendasi_raw, gap_skills = CVAnalyzerService.analisis(
            payload.teks_cv, kategori
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat analisis CV: {str(e)}",
        )

    rekomendasi = [RekomendasiRole(**r) for r in rekomendasi_raw]

    return PredictionResponse(
        kategori=kategori,
        confidence=round(confidence, 2),
        skills=skills,
        rekomendasi=rekomendasi,
        gap_skills=gap_skills,
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Cek status model",
    tags=["Health"],
)
def health_check():
    """Mengecek apakah model sudah dimuat dan siap menerima prediksi."""
    model_ready = CVPredictionService._model is not None
    return {
        "status": "ready" if model_ready else "not_ready",
        "model_loaded": model_ready,
    }