# CV Job Category Predictor API

API berbasis FastAPI untuk memprediksi kategori pekerjaan dari teks CV menggunakan model TensorFlow.

## Struktur Project

```
cv_predictor/
├── main.py                          # Entrypoint FastAPI
├── requirements.txt
├── .env.example
├── .gitignore
├── model/                           # Letakkan file model di sini
│   ├── model.keras
│   └── encoder.pkl
└── app/
    ├── api/
    │   └── routes.py                # Endpoint API
    ├── core/
    │   └── config.py                # Konfigurasi & settings
    ├── schemas/
    │   └── cv_schema.py             # Pydantic request/response
    └── services/
        └── cv_prediction_service.py # Logika prediksi ML
```

## Instalasi

```bash
# 1. Clone / ekstrak project
cd cv_predictor

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Salin dan isi .env
cp .env.example .env
# Edit .env, sesuaikan MODEL_PATH dan ENCODER_PATH

# 5. Letakkan file model
# Salin model.keras dan encoder.pkl ke folder model/
```

## Menjalankan Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint

| Method | URL | Deskripsi |
|--------|-----|-----------|
| `GET`  | `/` | Info aplikasi |
| `GET`  | `/api/v1/health` | Status model |
| `POST` | `/api/v1/predict` | Prediksi kategori CV |

## Contoh Request

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "teks_cv": "Nama: Budi Santoso. Pengalaman 3 tahun sebagai Data Analyst. Keahlian Python, SQL, Tableau."
  }'
```

## Contoh Response

```json
{
  "kategori": "Data Science",
  "confidence": 94.72,
  "status": "success"
}
```

## Dokumentasi Interaktif

Setelah server berjalan, buka:
- Swagger UI : http://localhost:8000/docs
- ReDoc      : http://localhost:8000/redoc
