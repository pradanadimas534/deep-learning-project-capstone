from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from engine import handler
import uvicorn

# Skema Request: Backend Laravel akan mengirimkan JSON {"text": "isi cv..."}
class CvRequest(BaseModel):
    text: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Mengatur startup aplikasi (memuat model sekali saja)."""
    success = handler.load_components()
    if not success:
        print("🛑 PERINGATAN: Server berjalan tanpa model!")
    yield
    print("Shutting down server...")

# Inisialisasi FastAPI
app = FastAPI(
    title="CV Recommendation API",
    description="API untuk klasifikasi lowongan berdasarkan scan teks CV",
    lifespan=lifespan
)

@app.get("/")
async def health_check():
    return {"status": "online", "message": "API siap menerima request"}

@app.post("/predict")
async def get_recommendation(request: CvRequest):
    # Validasi jika teks kosong
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Teks CV tidak boleh kosong")

    try:
        # Jalankan prediksi melalui handler
        result = handler.predict(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Penting: reload=False untuk menghindari penguncian file oleh sistem Windows
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)