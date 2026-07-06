---
title: CV Job Category Predictor
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# CV Job Category Predictor API

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi)
![Keras](https://img.shields.io/badge/Keras-3.14.0-red?logo=keras)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18+-orange?logo=tensorflow)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-yellow?logo=huggingface)

API berbasis **FastAPI** untuk menganalisis teks CV dan menghasilkan:
- **Prediksi kategori pekerjaan** menggunakan model Deep Learning (Keras 3)
- **Deteksi skill** dari teks CV
- **Rekomendasi lowongan asli** dari dataset berdasarkan match skill
- **Gap skills** yang perlu ditingkatkan

---

## Cara Kerja

```
Teks CV (plain text)
        │
        ▼
┌───────────────────┐
│   Model Keras 3   │  ──► Prediksi kategori + confidence
│  (TextVectorize   │
│  + Embedding      │
│  + ResidualBlock) │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  CV Analyzer      │  ──► Scan skill dari teks CV
│  (dari dataset    │  ──► Hitung match % vs lowongan
│   CSV asli)       │  ──► Hitung gap skills
└───────────────────┘
        │
        ▼
   Response JSON
```

---

## Struktur Project

```
cv_predictor/
├── main.py
├── Dockerfile
├── requirements.txt
├── .env.example
├── model/
│   ├── model.keras            # Upload manual
│   └── label_encoder.pkl      # Upload manual
├── data/
│   └── all_jobs_data.csv      # Upload manual
└── app/
    ├── api/routes.py
    ├── core/config.py
    ├── schemas/cv_schema.py
    └── services/
        ├── cv_prediction_service.py
        └── cv_analyzer_service.py
```

---

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework API | FastAPI 0.111.0 |
| ML Framework | Keras 3.14.0 + TensorFlow 2.18+ |
| Data Processing | Pandas, NumPy |
| Label Encoding | Scikit-learn |
| Deployment | Docker + Hugging Face Spaces |
| Python | 3.12 |

---

## Instalasi Lokal

```bash
# 1. Clone repository
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Salin konfigurasi
cp .env.example .env

# 5. Taruh file model & data
#    model/model.keras
#    model/label_encoder.pkl
#    data/all_jobs_data.csv

# 6. Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Variables

```env
APP_NAME="CV Job Category Predictor"
APP_VERSION="1.0.0"
MODEL_PATH="model/model.keras"
ENCODER_PATH="model/label_encoder.pkl"
DATASET_PATH="data/all_jobs_data.csv"
ALLOWED_ORIGINS="*"
```

---

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/` | Info aplikasi |
| `GET` | `/api/v1/health` | Status model dan data |
| `POST` | `/api/v1/predict` | Prediksi dari teks CV |

### POST `/api/v1/predict`

**Request:**
```json
{
  "teks_cv": "Nama: Budi Santoso. Pengalaman 3 tahun sebagai Software Engineer. Menguasai Python, React, Docker, AWS, PostgreSQL, dan Git."
}
```

**Response sukses:**
```json
{
  "kategori": "Software",
  "confidence": 91.3,
  "is_valid": true,
  "pesan": null,
  "skills": ["Python", "React", "Docker", "AWS"],
  "rekomendasi": [
    {
      "job_title": "Software Engineer",
      "company": "PT Tech Indonesia",
      "location": "Jakarta",
      "salary": 15000000,
      "skills_dibutuhkan": ["Python", "React", "Docker", "AWS", "Git"],
      "match": 80
    }
  ],
  "gap_skills": ["Kubernetes", "TypeScript", "Redis"],
  "status": "success"
}
```

**Response tidak valid:**
```json
{
  "kategori": "Marketing",
  "confidence": 55.2,
  "is_valid": false,
  "pesan": "Confidence prediksi terlalu rendah (55.2%). Minimal 70.0%.",
  "skills": [],
  "rekomendasi": [],
  "gap_skills": [],
  "status": "success"
}
```

---

## Arsitektur Model

```
Input (string)
    │
TextVectorization (vocab: 5000, seq_len: 50)
    │
Embedding (dim: 64, mask_zero: True)
    │
GlobalMaxPooling1D
    │
CustomResidualBlock (units: 64)
    │   Dense(64,relu) → Dense(64) → LayerNorm → Add(shortcut) → ReLU
Dropout (0.3)
    │
CustomResidualBlock (units: 32)
    │   Dense(32,relu) → Dense(32) → LayerNorm → Add(projection) → ReLU
Dropout (0.2)
    │
Dense(8, softmax)
```

**Kategori:** `Software` · `Technology` · `Finance` · `Healthcare` · `Marketing` · `Manufacturing` · `Retail` · `Education`

---

## Deploy ke Hugging Face Spaces

```bash
git lfs install
git clone https://huggingface.co/spaces/<username>/<space-name>
cd <space-name>
cp -r /path/to/cv_predictor/* .
git lfs track "model/*.keras"
git lfs track "model/*.pkl"
git add .
git commit -m "deploy: initial"
git push
```

---

## Kontribusi

Project ini bagian dari **Capstone Project DBS Coding Camp** (AI/ML Learning Path) — program MBKM Studi Independen Bersertifikat.
