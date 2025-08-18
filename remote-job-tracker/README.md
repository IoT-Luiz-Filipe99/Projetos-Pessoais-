# 🌍 Remote Job Tracker (Scraping + Ranking + UI + API)

Coleta vagas **remotas**, normaliza, armazena em **SQLite**, oferece **API (FastAPI)**, **UI (Streamlit)** com ranking por **match de skills (TF-IDF)** e script de execução diária.

## ✨ Features
- Scraper de **RemoteOK** (API pública), com User-Agent e backoff
- Normalização dos campos para um schema único
- Banco **SQLite** via SQLAlchemy
- **API**: listar vagas, filtrar, salvar favoritas
- **UI**: filtros, ranking por match, salvar e exportar CSV
- **Tests** básicos de parser e ranking
- **CI** (GitHub Actions)

## 🚀 Como rodar
```bash
# 1) clone e entre
git clone https://github.com/SEUUSUARIO/remote-job-tracker && cd remote-job-tracker

# 2) venv + deps
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) ETL (extrair -> normalizar -> carregar)
python -m src.etl.extract_remoteok
python -m src.etl.normalize
python -m src.etl.load

# 4) API
uvicorn src.api.main:app --reload

# 5) UI
streamlit run src/ui/app.py
