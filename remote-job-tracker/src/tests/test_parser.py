import json
from pathlib import Path
from src.etl.normalize import normalize_remoteok

def test_normalize_remoteok_empty():
    df = normalize_remoteok([])
    assert df.empty

def test_normalize_remoteok_basic(tmp_path):
    sample = [{
        "position": "Python Developer",
        "company": "Acme",
        "location": "Remote",
        "tags": ["python", "fastapi"],
        "salary": "$3k-$5k",
        "url": "https://remoteok.com/123",
        "description": "Build APIs with FastAPI.",
        "date": "2025-08-01"
    }]
    df = normalize_remoteok(sample)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["title"] == "Python Developer"
    assert "python" in row["stack"]
    assert row["url"].startswith("http")
