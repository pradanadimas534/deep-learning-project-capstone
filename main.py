from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF

from engine import InferenceEngine

app = FastAPI(title="AI Job Recommendation API 🚀")

engine = InferenceEngine()

# =====================
# CORS (biar frontend bisa akses)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# ROOT
# =====================
@app.get("/")
def home():
    return {"message": "AI Job Recommendation API is running 🚀"}

# =====================
# PREDICT DARI TEXT
# =====================
@app.post("/predict")
async def predict_text(data: dict):
    text = data.get("cv_text", "")

    if not text:
        return {"error": "cv_text is required"}

    results = engine.predict(text)

    return {
        "input": text,
        "recommendations": results
    }

# =====================
# PREDICT DARI PDF CV
# =====================
@app.post("/scan-cv")
async def scan_cv(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()

        results = engine.predict(text)

        return {
            "filename": file.filename,
            "recommendations": results
        }

    except Exception as e:
        return {"error": str(e)}