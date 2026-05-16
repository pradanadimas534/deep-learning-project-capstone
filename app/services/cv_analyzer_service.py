"""
cv_analyzer_service.py
----------------------
Load langsung dari all_jobs_data.csv.
Menghasilkan:
  - skills yang terdeteksi dari teks CV
  - rekomendasi role + perusahaan + skill yang dibutuhkan + match %
  - gap skills
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from app.core.config import settings

CONFIDENCE_THRESHOLD = 70.0


class CVAnalyzerService:
    _df: pd.DataFrame = None

    @classmethod
    def _load_csv(cls) -> None:
        """Load CSV dataset sekali saat pertama dipakai (lazy singleton)."""
        if cls._df is None:
            csv_path = Path(settings.DATASET_PATH)
            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Dataset CSV tidak ditemukan di: {csv_path}"
                )
            cls._df = pd.read_csv(csv_path)
            print(f"[INFO] Dataset dimuat: {len(cls._df):,} baris dari {csv_path}")

    @staticmethod
    def _parse_skills(s: str) -> List[str]:
        """Parse skills_list dari format Python list string atau CSV string."""
        try:
            result = ast.literal_eval(s)
            if isinstance(result, list):
                return [str(x).strip() for x in result]
        except Exception:
            pass
        return [x.strip() for x in str(s).split(",") if x.strip()]

    @classmethod
    def _semua_skill_kategori(cls, kategori: str) -> set:
        """Ambil semua skill unik dari seluruh baris di kategori tersebut."""
        subset = cls._df[cls._df["category"] == kategori]
        skill_pool: set = set()
        for s in subset["skills_list"].dropna():
            skill_pool.update(cls._parse_skills(s))
        return skill_pool

    @classmethod
    def ekstrak_skills(cls, teks_cv: str, kategori: str) -> List[str]:
        """
        Scan teks CV dan temukan skill yang ada di kategori dataset.
        Case-insensitive dengan word boundary.
        """
        cls._load_csv()
        skill_pool = cls._semua_skill_kategori(kategori)
        teks_lower = teks_cv.lower()
        ditemukan = []
        for skill in skill_pool:
            pola = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pola, teks_lower):
                ditemukan.append(skill)
        return ditemukan

    @classmethod
    def cari_rekomendasi(
        cls, kategori: str, skills_dimiliki: List[str], top_n: int = 5
    ) -> List[Dict]:
        """
        Cari lowongan dari dataset yang paling cocok dengan skill CV.

        Tiap item hasil berisi:
          - job_title    : nama posisi
          - company      : nama perusahaan
          - location     : lokasi
          - salary       : gaji (jika ada)
          - skills_dibutuhkan : skill yang dibutuhkan perusahaan untuk posisi ini
          - match        : % kesesuaian skill CV vs skill dibutuhkan

        Hanya lowongan dengan match > 0 yang dikembalikan.
        """
        cls._load_csv()

        if not skills_dimiliki:
            return []

        subset = cls._df[cls._df["category"] == kategori]
        if subset.empty:
            return []

        skills_cv = set(s.lower() for s in skills_dimiliki)
        hasil = []

        for _, row in subset.iterrows():
            skills_job = cls._parse_skills(str(row.get("skills_list", "")))
            if not skills_job:
                continue

            skills_job_lower = set(s.lower() for s in skills_job)
            cocok = len(skills_cv & skills_job_lower)
            match = round((cocok / len(skills_job_lower)) * 100)

            if match > 0:
                hasil.append({
                    "job_title":         str(row.get("job_title", "-")),
                    "company":           str(row.get("company", "-")),
                    "location":          str(row.get("location", "-")),
                    "salary":            row.get("salary", None),
                    "skills_dibutuhkan": skills_job,
                    "match":             match,
                })

        hasil.sort(key=lambda x: x["match"], reverse=True)
        return hasil[:top_n]

    @classmethod
    def hitung_gap_skills(
        cls, kategori: str, skills_dimiliki: List[str]
    ) -> List[str]:
        """
        Gap = skill yang paling banyak dibutuhkan di kategori ini
        tapi belum dimiliki pelamar. Diurutkan dari yang paling sering
        dibutuhkan. Maksimal 8.
        """
        cls._load_csv()

        from collections import Counter
        subset = cls._df[cls._df["category"] == kategori]
        counter: Counter = Counter()
        for s in subset["skills_list"].dropna():
            counter.update(cls._parse_skills(s))

        skills_lower = set(s.lower() for s in skills_dimiliki)
        gap = [
            skill for skill, _ in counter.most_common()
            if skill.lower() not in skills_lower
        ]
        return gap[:8]

    @classmethod
    def _get_sample_skills(cls, kategori: str, n: int = 5) -> List[str]:
        """Ambil contoh skill dari kategori untuk ditampilkan di pesan."""
        cls._load_csv()
        from collections import Counter
        subset = cls._df[cls._df["category"] == kategori]
        counter: Counter = Counter()
        for s in subset["skills_list"].dropna():
            counter.update(cls._parse_skills(s))
        return [skill for skill, _ in counter.most_common(n)]

    @classmethod
    def analisis(
        cls, teks_cv: str, kategori: str, confidence: float
    ) -> Tuple[List[str], List[Dict], List[str], bool]:
        """
        Entry point utama.

        Returns:
            Tuple(skills, rekomendasi, gap_skills, is_valid)
        """
        skills   = cls.ekstrak_skills(teks_cv, kategori)
        is_valid = confidence >= CONFIDENCE_THRESHOLD and len(skills) > 0

        if not is_valid:
            return skills, [], [], False

        rekomendasi = cls.cari_rekomendasi(kategori, skills)
        gap_skills  = cls.hitung_gap_skills(kategori, skills)
        return skills, rekomendasi, gap_skills, True