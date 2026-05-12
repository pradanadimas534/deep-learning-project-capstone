"""
build_skill_reference.py
------------------------
Jalankan script ini SATU KALI untuk membangun skill_reference.json
dari dataset CSV.

Cara pakai:
    python build_skill_reference.py
    python build_skill_reference.py --csv path/to/data.csv --output model/skill_reference.json

Output:
    model/skill_reference.json
"""

import argparse
import ast
import json
import os

import pandas as pd


def parse_skills(s: str) -> list:
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return [str(x).strip() for x in result]
    except Exception:
        pass
    return [x.strip() for x in str(s).split(",") if x.strip()]


def build_reference(csv_path: str) -> dict:
    print(f"[INFO] Membaca dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    required_cols = {"category", "skills_list", "job_title"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Kolom tidak ditemukan di CSV: {missing}")

    print(f"[INFO] Total data   : {len(df):,} baris")
    print(f"[INFO] Kategori     : {sorted(df['category'].unique().tolist())}")

    reference = {}

    for cat in sorted(df["category"].unique()):
        subset = df[df["category"] == cat]

        # Semua skill unik untuk kategori ini (dipakai untuk gap skills)
        all_cat_skills: set = set()
        for s in subset["skills_list"].dropna():
            all_cat_skills.update(parse_skills(s))

        # Per job_title: kumpulkan skill unik yang dibutuhkan
        roles = {}
        for title in subset["job_title"].value_counts().index:
            jobs = subset[subset["job_title"] == title]
            skills_role: set = set()
            for s in jobs["skills_list"].dropna():
                skills_role.update(parse_skills(s))
            if skills_role:
                roles[title] = sorted(skills_role)

        reference[cat] = {
            "skills_ideal": sorted(all_cat_skills),
            "roles": roles,
            "total_jobs": len(subset),
        }

        print(
            f"  ✓ {cat}: {len(roles)} roles, "
            f"{len(all_cat_skills)} skill unik, "
            f"{len(subset):,} jobs"
        )

    return reference


def main():
    parser = argparse.ArgumentParser(
        description="Build skill_reference.json dari dataset CSV"
    )
    parser.add_argument("--csv", default="all_jobs_data.csv")
    parser.add_argument("--output", default="model/skill_reference.json")
    args = parser.parse_args()

    reference = build_reference(args.csv)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Berhasil disimpan ke: {args.output}")


if __name__ == "__main__":
    main()
