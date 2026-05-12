"""
cv_analyzer_service.py
----------------------
Menganalisis teks CV berdasarkan skill_reference.json yang dibangun
dari dataset CSV asli.

Alur:
  1. Model TF prediksi kategori (misal: "Software")
  2. Lookup ke skill_reference.json → ambil semua roles + skill per role
     di kategori tersebut
  3. Hitung match % CV vs skill tiap role dari dataset
  4. Kembalikan rekomendasi role + skills dimiliki + gap skills
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from app.core.config import settings


class CVAnalyzerService:
    _reference: Dict = {}

    @classmethod
    def _load_reference(cls) -> None:
        """Muat skill_reference.json sekali (lazy singleton)."""
        if not cls._reference:
            ref_path = Path(settings.SKILL_REFERENCE_PATH)
            if not ref_path.exists():
                raise FileNotFoundError(
                    f"skill_reference.json tidak ditemukan di: {ref_path}\n"
                    "Jalankan dulu: python build_skill_reference.py"
                )
            with open(ref_path, "r", encoding="utf-8") as f:
                cls._reference = json.load(f)
            print(f"[INFO] Skill reference dimuat: {list(cls._reference.keys())}")

    @classmethod
    def _scan_skills_dari_teks(cls, teks_cv: str, skill_pool: set) -> List[str]:
        """
        Scan teks CV dan temukan skill yang ada di skill_pool.
        Case-insensitive, pakai word boundary agar tidak salah deteksi.
        """
        teks_lower = teks_cv.lower()
        ditemukan = []
        for skill in skill_pool:
            pola = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pola, teks_lower):
                ditemukan.append(skill)
        return ditemukan

    @classmethod
    def ekstrak_skills(cls, teks_cv: str, kategori: str) -> List[str]:
        """
        Temukan skill dari teks CV yang relevan dengan kategori prediksi.
        Dibandingkan langsung dengan skills_ideal kategori di dataset.
        """
        cls._load_reference()
        skill_pool = set(
            cls._reference.get(kategori, {}).get("skills_ideal", [])
        )
        return cls._scan_skills_dari_teks(teks_cv, skill_pool)

    @classmethod
    def hitung_rekomendasi(
        cls, kategori: str, skills_dimiliki: List[str]
    ) -> List[Dict]:
        """
        Hitung match % CV vs skill yang dibutuhkan tiap role di dataset.

        Formula:
            match % = (skill CV yang cocok / total skill dibutuhkan role) * 100

        Hanya role dengan match > 0 yang dikembalikan.
        Diurutkan dari match tertinggi, maksimal 5 role teratas.
        """
        cls._load_reference()

        roles: Dict = cls._reference.get(kategori, {}).get("roles", {})
        if not roles:
            return [{"role": "General Professional", "match": 0}]

        skills_cv = set(s.lower() for s in skills_dimiliki)
        hasil = []

        for role_name, skills_dibutuhkan in roles.items():
            if not skills_dibutuhkan:
                continue

            skills_role_lower = set(s.lower() for s in skills_dibutuhkan)
            cocok = len(skills_cv & skills_role_lower)
            match = round((cocok / len(skills_role_lower)) * 100)

            if match > 0:
                hasil.append({"role": role_name, "match": match})

        if not hasil:
            # Kalau tidak ada skill yang cocok sama sekali, tampilkan top 5 dengan match 0
            top5 = list(roles.keys())[:5]
            return [{"role": r, "match": 0} for r in top5]

        # Urutkan dari match tertinggi, ambil top 5
        hasil.sort(key=lambda x: x["match"], reverse=True)
        return hasil[:5]

    @classmethod
    def hitung_gap_skills(
        cls, kategori: str, skills_dimiliki: List[str]
    ) -> List[str]:
        """
        Gap skills = skill ideal kategori yang belum dimiliki pelamar.
        Diambil dari skills_ideal kategori di dataset, maksimal 8.
        """
        cls._load_reference()

        skills_ideal = cls._reference.get(kategori, {}).get("skills_ideal", [])
        skills_lower = set(s.lower() for s in skills_dimiliki)

        gap = [s for s in skills_ideal if s.lower() not in skills_lower]
        return gap[:8]

    @classmethod
    def analisis(
        cls, teks_cv: str, kategori: str
    ) -> Tuple[List[str], List[Dict], List[str]]:
        """
        Entry point utama.

        Returns:
            Tuple(skills_dimiliki, rekomendasi_role, gap_skills)
        """
        skills = cls.ekstrak_skills(teks_cv, kategori)
        rekomendasi = cls.hitung_rekomendasi(kategori, skills)
        gap_skills = cls.hitung_gap_skills(kategori, skills)
        return skills, rekomendasi, gap_skills
