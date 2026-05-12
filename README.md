ZIP siap diunduh. Isi lengkapnya:

```
cv_predictor/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── model/                  ← taruh model.keras & encoder.pkl di sini
└── app/
    ├── api/routes.py
    ├── core/config.py
    ├── schemas/cv_schema.py
    └── services/cv_prediction_service.py
```

**Langkah setelah ekstrak:**

```bash
# Install dependencies
pip install -r requirements.txt

# Salin & isi konfigurasi
cp .env.example .env

# Taruh model ke folder model/
# model/model.keras
# model/encoder.pkl

# Jalankan
uvicorn main:app --reload
```

Swagger docs otomatis tersedia di `http://localhost:8000/docs`.
