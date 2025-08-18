from __future__ import annotations
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "jobs.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

app = FastAPI(title="Remote Job Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class SaveJobReq(BaseModel):
    job_id: int
    note: str | None = None

@app.get("/")
def root():
    return {"name": "Remote Job Tracker API", "status": "ok"}

@app.get("/jobs")
def list_jobs(q: str | None = None, company: str | None = None, min_match: float | None = Query(None, ge=0, le=100)):
    # leitura básica
    with engine.begin() as conn:
        df = pd.read_sql("select * from jobs order by id desc", conn)
    if q:
        ql = q.lower()
        df = df[df["title"].str.lower().str.contains(ql) | df["description"].str.lower().str.contains(ql)]
    if company:
        df = df[df["company"].str.contains(company, case=False, na=False)]
    if min_match is not None and "match" in df.columns:
        df = df[df["match"] >= min_match]
    return df.fillna("").to_dict(orient="records")

@app.post("/save")
def save_job(req: SaveJobReq):
    with engine.begin() as conn:
        job = conn.execute(text("select id from jobs where id=:i"), {"i": req.job_id}).first()
        if not job:
            raise HTTPException(404, "Job não encontrado")
        conn.execute(text("insert into saved_jobs(job_id, note) values (:i,:n)"), {"i": req.job_id, "n": req.note or ""})
    return {"ok": True}

@app.get("/saved")
def saved_jobs():
    with engine.begin() as conn:
        rows = conn.execute(text("""
            select s.id as saved_id, j.*
            from saved_jobs s join jobs j on j.id = s.job_id
            order by s.id desc
        """)).mappings().all()
    return [dict(r) for r in rows]
