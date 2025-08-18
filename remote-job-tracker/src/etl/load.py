"""
Carrega data/normalized_jobs.csv para SQLite.
Cria tabelas: jobs, saved_jobs.
"""
from __future__ import annotations
import pathlib, sys
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "normalized_jobs.csv"
DB_PATH = BASE_DIR / "jobs.db"

DDL = """
create table if not exists jobs (
  id integer primary key autoincrement,
  source text,
  title text,
  company text,
  location text,
  remote integer,
  seniority text,
  stack text,
  salary text,
  url text unique,
  description text,
  published_at text,
  created_at text default (datetime('now'))
);

create table if not exists saved_jobs (
  id integer primary key autoincrement,
  job_id integer references jobs(id) on delete cascade,
  note text,
  created_at text default (datetime('now'))
);
"""

def main():
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    with engine.begin() as conn:
        for stmt in DDL.strip().split(";\n\n"):
            if stmt.strip():
                conn.execute(text(stmt))
        if CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH)
            df["remote"] = df["remote"].astype(int)
            df.to_sql("jobs", conn, if_exists="append", index=False, method="multi")
    print(f"[ok] DB atualizado em {DB_PATH}")

if __name__ == "__main__":
    sys.exit(main())
