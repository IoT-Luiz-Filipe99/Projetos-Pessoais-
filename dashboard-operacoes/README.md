# 📊 Dashboard de Operações (Streamlit + Supabase)

KPIs, filtros, gráficos interativos e exportação de dados. Pronto para **dados sintéticos** ou **Supabase**.

## 🚀 Demo local (modo fake)
```bash
# clonar e entrar
git clone https://github.com/SEUUSUARIO/dashboard-operacoes && cd dashboard-operacoes

# criar venv e instalar deps
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# configurar .env
cp .env.example .env
# (por padrão, USE_FAKE_DATA=true)

# gerar dados sintéticos
python scripts/seed_data.py

# rodar
streamlit run src/app/main.py
