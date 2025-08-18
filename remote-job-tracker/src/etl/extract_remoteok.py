
---

## 🧱 `src/etl/extract_remoteok.py`
```python
"""
Extrator de vagas remotas a partir da API pública do RemoteOK.
Saída: data/raw_remoteok.json (lista JSON de vagas)
"""
from __future__ import annotations
import os, time, json, pathlib, sys
import requests

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "raw_remoteok.json"

REMOTEOK_API = os.getenv("REMOTEOK_API", "https://remoteok.com/api")
USER_AGENT = os.getenv("USER_AGENT", "RemoteJobTracker/1.0 (+https://github.com/SEUUSUARIO)")

def fetch_remoteok() -> list[dict]:
    # backoff simples
    for attempt in range(3):
        try:
            resp = requests.get(REMOTEOK_API, headers={"User-Agent": USER_AGENT}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            # a API retorna o primeiro item como metadados; removemos
            if isinstance(data, list) and data and isinstance(data[0], dict) and "legal" in data[0]:
                data = data[1:]
            return data if isinstance(data, list) else []
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    return []

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    jobs = fetch_remoteok()
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[ok] {len(jobs)} vagas salvas em {RAW_PATH}")

if __name__ == "__main__":
    sys.exit(main())
