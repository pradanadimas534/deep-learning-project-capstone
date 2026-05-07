from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import router
from app.core.config import settings
from app.services.cv_prediction_service import CVPredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Muat model saat startup, cleanup saat shutdown."""
    print("[STARTUP] Memuat model ML...")
    CVPredictionService.load_model()
    print("[STARTUP] Model siap!")
    yield
    print("[SHUTDOWN] Aplikasi berhenti.")


app = FastAPI(
    title=settings.APP_NAME,
    description="API untuk memprediksi kategori pekerjaan dari teks CV.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
