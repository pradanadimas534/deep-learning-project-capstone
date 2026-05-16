from fastapi import APIRouter, HTTPException, status

from app.schemas.cv_schema import CVTextRequest, PredictionResponse, RekomendasiItem
from app.services.cv_prediction_service import CVPredictionService
from app.services.cv_analyzer_service import CVAnalyzerService, CONFIDENCE_THRESHOLD

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Prediksi kategori + rekomendasi lowongan asli",
    tags=["Prediction"],
)
def predict_cv(payload: CVTextRequest) -> PredictionResponse:

    # Step 1 — Prediksi kategori dari model TF
    try:
        kategori, confidence = CVPredictionService.predict(payload.teks_cv)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error prediksi: {str(e)}")

    # Step 2 — Analisis skill + rekomendasi + gap
    try:
        skills, rekomendasi_raw, gap_skills, is_valid = CVAnalyzerService.analisis(
            payload.teks_cv, kategori, confidence
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analisis: {str(e)}")

    # Pesan jika tidak valid
    pesan = None
    if not is_valid:
        if confidence < CONFIDENCE_THRESHOLD:
            pesan = (
                f"Confidence prediksi terlalu rendah ({confidence:.1f}%). "
                f"Minimal {CONFIDENCE_THRESHOLD}%. "
                "Coba lengkapi CV dengan pengalaman dan skill yang lebih detail."
            )
        elif len(skills) == 0:
            contoh = ", ".join(CVAnalyzerService._get_sample_skills(kategori))
            pesan = (
                f"Skill dari CV tidak cocok dengan kategori '{kategori}'. "
                f"Contoh skill yang dibutuhkan: {contoh}."
            )

    rekomendasi = [RekomendasiItem(**r) for r in rekomendasi_raw]

    return PredictionResponse(
        kategori=kategori,
        confidence=round(confidence, 2),
        is_valid=is_valid,
        pesan=pesan,
        skills=skills,
        rekomendasi=rekomendasi,
        gap_skills=gap_skills,
    )


@router.get("/health", tags=["Health"], summary="Cek status model dan data")
def health_check():
    return {
        "status":       "ready" if CVPredictionService._model is not None else "not_ready",
        "model_loaded": CVPredictionService._model is not None,
        "data_loaded":  CVAnalyzerService._df is not None,
    }