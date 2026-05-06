## ⚙️ Cara Menjalankan
Karena kebijakan keamanan pada sistem operasi tertentu (khususnya Windows), ikuti langkah-langkah berikut untuk menghindari masalah izin akses (*Permission Denied*):

1.  **Buka Terminal sebagai Administrator**: Cari PowerShell atau CMD, klik kanan dan pilih **Run as Administrator**.
2.  **Masuk ke Direktori Proyek**:
    ```powershell
    cd C:\Users\dimas\Documents\Code\Codding\deep-learning-project-capstone
    ```
3.  **Jalankan API**:
    ```powershell
    python main.py
    ```
4.  **Verifikasi**: Pastikan muncul pesan `✅ AI Components Loaded Successfully!` di terminal Anda.

## 🧪 Cara Testing
Setelah server berjalan di `http://127.0.0.1:8000`, Anda bisa melakukan tes dengan cara:

### 1. Dokumentasi Interaktif (Swagger UI)
Buka browser dan akses: `http://127.0.0.1:8000/docs`
Gunakan tombol **Try it out** pada endpoint `POST /predict`.

### 2. Contoh Request (JSON)
Kirimkan permintaan POST ke `http://127.0.0.1:Berikut adalah draf file **README.md** yang profesional untuk proyek Anda. File ini disusun agar tim backend atau penguji lainnya dapat menjalankan API rekomendasi lowongan kerja Anda tanpa hambatan teknis.

---

# CV Recommendation API (Deep Learning)

API ini dikembangkan menggunakan **FastAPI** dan **TensorFlow** untuk memberikan rekomendasi posisi pekerjaan berdasarkan ekstraksi teks dari CV. Proyek ini merupakan bagian dari sistem rekomendasi lowongan kerja cerdas.

## 🚀 Fitur Utama
*   **Inference Model Deep Learning**: Menggunakan model Keras untuk klasifikasi teks secara *real-time*.
*   **FastAPI Framework**: Performa tinggi, mudah digunakan, dan dokumentasi otomatis (Swagger UI).
*   **Standardized JSON Output**: Memudahkan integrasi dengan berbagai backend (Laravel, Node.js, dll).

## 🛠️ Prasyarat
Pastikan Anda sudah menginstal dependensi berikut pada lingkungan Python Anda:
```bash
pip install fastapi uvicorn tensorflow numpy
