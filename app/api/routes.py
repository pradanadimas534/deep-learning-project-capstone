from fastapi import APIRouter, HTTPException, status

from app.schemas.cv_schema import CVTextRequest, PredictionResponse
from app.services.cv_prediction_service import CVPredictionService

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Prediksi kategori pekerjaan dari teks CV",
    description=(
        "Menerima teks CV dalam bentuk plain text dan mengembalikan "
        "prediksi kategori pekerjaan beserta confidence score-nya."
    ),
    tags=["Prediction"],
)
def predict_cv(payload: CVTextRequest) -> PredictionResponse:
    """
    **Request body:**
    - `teks_cv` – Isi teks CV (minimal 10 karakter).

    **Response:**
    - `kategori`   – Kategori pekerjaan hasil prediksi.
    - `confidence` – Tingkat keyakinan model dalam persen (0–100).
    - `status`     – `"success"` jika berhasil.
    """
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
            detail=f"Terjadi kesalahan internal: {str(e)}",
        )

    return PredictionResponse(
        kategori=kategori,
        confidence=round(confidence, 2),
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
