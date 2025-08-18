import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from supabase import create_client

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(layout="wide", page_title="Dashboard Futura Tecnologia")

# === INSERE CSS COM LOGO AO FUNDO ===
def add_background_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        body {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: 350px;
            background-repeat: no-repeat;
            background-position: right bottom;
            background-attachment: fixed;
        }}
        .metric-card {{
            background-color: #f9f9f9;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0px 0px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        .stButton button {{
            background-color: #0077B6;
            color: white;
            padding: 0.5em 1.5em;
            border-radius: 10px;
            font-weight: bold;
            border: none;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_background_from_local("logo_futura.png")

# === PROJETOS E CONEXÃO COM SUPABASE ===
projetos = ["AMERICANAS", "DELFIA-TELMEX", "FUST-CLARO-MS", "FUST-CLARO-RJ", "MULT-PROJETOS"]
url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODk5NzgyNSwiZXhwIjoyMDY0NTczODI1fQ.TjwW4ztaD6CwFIDOK8aKm10VcgRvUZasMbst7Yiq3h0"
supabase = create_client(url, key)

# === CARREGA E UNIFICA OS DADOS ===
dfs = []
for nome in projetos:
    data = supabase.table(nome).select("*").execute().data
    df = pd.DataFrame(data)
    df["Cliente"] = nome
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)
df = df[df["Agendado"] != "Agendado"]

# === CONVERSÃO DE DATA E NÚMEROS ===
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

colunas_numericas = [
    "Agendado", "agendado para hoje", "Em Campo", "finalizado",
    "Prospectar Técnico", "Valores", "pendente agendamento", "id",
    "total pago hoje - dos chamados de hoje",
    "valor a pagar - finalizados hoje",
    "valor a pagar total"
]
for col in colunas_numericas:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("R\$", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# === INTERFACE DO FILTRO DE DATA ===
datas_disponiveis = sorted(df["Date"].dropna().dt.date.unique())
data_selecionada = st.date_input("📅 Selecione uma data:", value=datas_disponiveis[-1], min_value=min(datas_disponiveis), max_value=max(datas_disponiveis))

# === TÍTULO DO DASHBOARD ===
st.markdown(f"<h1 style='color:#023e8a'>Dashboard Financeiro - Futura Tecnologia</h1>", unsafe_allow_html=True)
st.caption(f"Exibindo dados financeiros dos projetos na data: {data_selecionada.strftime('%d/%m/%Y')}")

# === LAYOUT COM GRÁFICOS POR PROJETO ===
cols = st.columns(len(projetos))

for i, projeto in enumerate(projetos):
    df_projeto = df[(df["Cliente"] == projeto) & (df["Date"].dt.date == data_selecionada)]

    pago = df_projeto["total pago hoje - dos chamados de hoje"].sum()
    apagar = df_projeto["valor a pagar - finalizados hoje"].sum()
    total = df_projeto["valor a pagar total"].sum()

    with cols[i]:
        st.markdown(f"### {projeto}")

        fig = go.Figure(data=[
            go.Bar(name='Pago', y=[''], x=[pago], orientation='h', marker_color='#0077B6'),
            go.Bar(name='A Pagar', y=[''], x=[apagar], orientation='h', marker_color='#90E0EF'),
        ])
        fig.update_layout(
            barmode='stack',
            height=110,
            margin=dict(l=0, r=0, t=20, b=20),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True, key=f"plot_{projeto}_{i}")

        st.markdown(f"""
        <div class="metric-card">
            <strong>💸 Pago:</strong><br> R$ {pago:,.2f}<br><br>
            <strong>📅 A Pagar:</strong><br> R$ {apagar:,.2f}<br><br>
            <strong>📊 Total Geral:</strong><br> R$ {total:,.2f}
        </div>
        """, unsafe_allow_html=True)
