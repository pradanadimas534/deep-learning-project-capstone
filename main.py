from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF

from engine import InferenceEngine

app = FastAPI()
engine = InferenceEngine()

# =====================
# CORS (biar frontend bisa akses)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# DUMMY JOB DATA
# =====================
MOCK_JOBS = [
    {"id": 1, "title": "Frontend Developer", "desc": "React JavaScript HTML CSS Tailwind"},
    {"id": 2, "title": "Backend Developer", "desc": "Python FastAPI PostgreSQL API Docker"},
    {"id": 3, "title": "Data Scientist", "desc": "Machine Learning Python Pandas Scikit-learn"},
]

# =====================
# ROOT ENDPOINT
# =====================
@app.get("/")
def home():
    return {"message": "AI Job Recommendation API 🚀"}

# =====================
# SCAN CV (UPLOAD PDF)
# =====================
@app.post("/scan-cv")
async def scan_cv(file: UploadFile = File(...)):
    try:
        # baca file PDF
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        cv_text = ""
        for page in doc:
            cv_text += page.get_text()

        # inference
        results = engine.predict(cv_text, MOCK_JOBS)

        return {
            "filename": file.filename,
            "recommendations": results
        }

    except Exception as e:
        return {"error": str(e)}

# =====================
# OPTIONAL: TEST TANPA PDF
# =====================
@app.post("/predict-text")
async def predict_text(data: dict):
    cv_text = data.get("cv_text", "")

    if not cv_text:
        return {"error": "cv_text is required"}

    results = engine.predict(cv_text, MOCK_JOBS)

    return {
        "input": cv_text,
        "recommendations": results
    }