"""
Normaliza raw_remoteok.json para um CSV tabular com colunas fixas.
Saída: data/normalized_jobs.csv
"""
from __future__ import annotations
import json, pathlib, sys
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "raw_remoteok.json"
CSV_PATH = DATA_DIR / "normalized_jobs.csv"

COLUMNS = [
    "source","title","company","location","remote","seniority",
    "stack","salary","url","description","published_at"
]

def normalize_remoteok(rows: list[dict]) -> pd.DataFrame:
    norm = []
    for r in rows:
        norm.append({
            "source": "remoteok",
            "title": r.get("position") or r.get("title") or "",
            "company": r.get("company") or "",
            "location": r.get("location") or (", ".join(r.get("location_tag", [])) if isinstance(r.get("location_tag"), list) else ""),
            "remote": True,
            "seniority": ", ".join(r.get("tags", [])) if isinstance(r.get("tags"), list) else "",
            "stack": ", ".join(r.get("tags", [])) if isinstance(r.get("tags"), list) else "",
            "salary": r.get("salary") or "",
            "url": r.get("url") or r.get("apply_url") or r.get("slug") or "",
            "description": r.get("description") or "",
            "published_at": r.get("date") or r.get("epoch") or "",
        })
    df = pd.DataFrame(norm, columns=COLUMNS)
    # limpeza básica
    df["title"] = df["title"].fillna("").str.strip()
    df["company"] = df["company"].fillna("").str.strip()
    df["url"] = df["url"].fillna("").str.strip()
    df["description"] = df["description"].fillna("").str.replace("\r", " ").str.replace("\n", " ").str.strip()
    return df.drop_duplicates(subset=["source","url"]).reset_index(drop=True)

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = json.load(open(RAW_PATH, "r", encoding="utf-8")) if RAW_PATH.exists() else []
    df = normalize_remoteok(rows)
    df.to_csv(CSV_PATH, index=False)
    print(f"[ok] {len(df)} vagas normalizadas em {CSV_PATH}")

if __name__ == "__main__":
    sys.exit(main())
