# CV Job Category Predictor API

API FastAPI untuk memprediksi kategori pekerjaan dari teks CV,
sekaligus memberikan rekomendasi role dan gap skills berdasarkan dataset asli.

## Cara Kerja

```
Teks CV masuk
     ↓
Model TF → prediksi kategori (misal: "Software")
     ↓
Lookup skill_reference.json (dibangun dari dataset CSV)
→ ambil semua role + skill yang dibutuhkan di kategori tersebut
     ↓
Hitung match % CV vs skill tiap role
     ↓
Output: kategori + confidence + skills + rekomendasi + gap_skills
```

## Struktur Project

```
cv_predictor/
├── main.py
├── build_skill_reference.py     ← jalankan SEKALI sebelum start server
├── requirements.txt
├── .env.example
├── model/
│   ├── model.keras              ← taruh di sini
│   ├── encoder.pkl              ← taruh di sini
│   └── skill_reference.json    ← digenerate oleh build_skill_reference.py
└── app/
    ├── api/routes.py
    ├── core/config.py
    ├── schemas/cv_schema.py
    └── services/
        ├── cv_prediction_service.py
        └── cv_analyzer_service.py
```

## Setup

```bash
# 1. Buat virtual environment Python 3.10
python3.10 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Salin konfigurasi
cp .env.example .env

# 4. Taruh model ke folder model/
#    model/model.keras  &  model/encoder.pkl

# 5. WAJIB — Build skill reference dari dataset CSV
python build_skill_reference.py --csv all_jobs_data.csv

# 6. Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Contoh Request

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"teks_cv": "Saya berpengalaman 3 tahun di bidang Software Engineering. Menguasai Python, React, Docker, AWS, dan SQL."}'
```

## Contoh Response

```json
{
  "kategori": "Software",
  "confidence": 91.3,
  "skills": ["Python", "React", "Docker", "AWS", "SQL"],
  "rekomendasi": [
    { "role": "Systems developer", "match": 71 },
    { "role": "Software Engineer", "match": 57 },
    { "role": "Machine Learning Engineer", "match": 42 }
  ],
  "gap_skills": ["Java", "C++", "Machine Learning"],
  "status": "success"
}
```

Dokumentasi Swagger: http://localhost:8000/docs
