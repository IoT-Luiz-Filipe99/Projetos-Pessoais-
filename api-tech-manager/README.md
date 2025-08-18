# 🔐 API Tech Manager (FastAPI + JWT + CRUD)

API com login seguro (bloqueio após tentativas), CRUD de Técnicos/Clientes/Ordens e upload de anexos (local/Supabase).

## 🚀 Rodando local
```bash
# 1) Clone
git clone https://github.com/SEUUSUARIO/api-tech-manager && cd api-tech-manager

# 2) Venv + deps
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) Config
cp .env.example .env
# (opcional) ajuste ALLOWED_ORIGINS e SECRET_KEY

# 4) Seed
python scripts/seed.py

# 5) Start
uvicorn src.app.main:app --reload
