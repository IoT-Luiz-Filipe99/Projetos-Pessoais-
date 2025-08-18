from __future__ import annotations
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Config page
st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Dashboard de Operações"),
    page_icon="📊",
    layout="wide"
)

# ------------- Helpers -------------
def load_fake_data(csv_path: str, days: int) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        st.warning("CSV sintético não encontrado. Rode: python scripts/seed_data.py")
        return pd.DataFrame(columns=["id","cliente","cidade","uf","status","criado_em","valor","categoria"])
    df = pd.read_csv(csv_path)
    # Convert types
    df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    # Filtro últimos N dias
    dt_from = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
    df = df[df["criado_em"] >= dt_from]
    return df.reset_index(drop=True)

@st.cache_data(show_spinner=False)
def get_data(days: int) -> pd.DataFrame:
    use_fake = os.getenv("USE_FAKE_DATA", "true").lower() == "true"
    if use_fake:
        return load_fake_data(os.getenv("FAKE_CSV_PATH", "./scripts/fake_chamados.csv"), days)
    else:
        from src.core.supabase_client import fetch_chamados_df
        table = os.getenv("SUPABASE_TABLE", "chamados")
        return fetch_chamados_df(table, days)

def kpi_card(label: str, value, help_text: str = ""):
    st.metric(label, value, help=help_text)

def to_csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# ------------- Sidebar -------------
st.sidebar.title("⚙️ Filtros")
default_days = int(os.getenv("DEFAULT_DATE_DAYS", "7"))
days = st.sidebar.slider("Intervalo (dias)", min_value=1, max_value=60, value=default_days, step=1)
search_cliente = st.sidebar.text_input("Buscar cliente")
status_opts_default = ["Agendado", "Em campo", "Finalizado", "Cancelado", "Pendente"]
status_select = st.sidebar.multiselect("Status", options=status_opts_default, default=status_opts_default)
uf_select = st.sidebar.text_input("Filtrar UF (ex: SP, RJ, MG)").upper().strip()

refresh_ms = int(os.getenv("AUTO_REFRESH_MS", "60000"))
st.sidebar.caption(f"🔄 Auto-refresh a cada {refresh_ms//1000}s")
st.sidebar.button("Forçar atualização", on_click=lambda: st.experimental_rerun())

# ------------- Data -------------
st.experimental_data_editor  # just to satisfy type checkers in some envs
st_autorefresh_id = st.experimental_rerun  # placeholder to avoid lint warning
st_autorefresh = st.experimental_memo  # placeholder for old versions

# Streamlit 1.38 tem st.autorefresh
try:
    st.autorefresh(interval=refresh_ms, key="auto_refresh")
except Exception:
    pass

df = get_data(days)

if not df.empty:
    # Normaliza status/categorias
    if "status" in df.columns:
        df["status"] = df["status"].fillna("Desconhecido").astype(str)
    if "cliente" in df.columns:
        df["cliente"] = df["cliente"].fillna("—").astype(str)

    # Filtros
    if search_cliente:
        df = df[df["cliente"].str.contains(search_cliente, case=False, na=False)]
    if status_select:
        df = df[df["status"].isin(status_select)]
    if uf_select:
        df = df[df.get("uf", "").astype(str).str.upper().eq(uf_select)]

# ------------- Header -------------
st.title(os.getenv("APP_TITLE", "Dashboard de Operações"))
st.caption("KPIs, filtros, gráficos interativos e exportação de dados.")

# ------------- KPIs -------------
col1, col2, col3, col4 = st.columns(4)
total = len(df)
finalizados = int((df["status"] == "Finalizado").sum()) if not df.empty and "status" in df.columns else 0
em_campo = int((df["status"] == "Em campo").sum()) if not df.empty and "status" in df.columns else 0
valor_total = float(df["valor"].sum()) if not df.empty and "valor" in df.columns else 0.0

with col1:
    kpi_card("Total de chamados", f"{total:,}".replace(",", "."))
with col2:
    kpi_card("Finalizados", f"{finalizados:,}".replace(",", "."))
with col3:
    kpi_card("Em campo", f"{em_campo:,}".replace(",", "."))
with col4:
    kpi_card("Valor total (R$)", f"{valor_total:,.2f}".replace(",", "."))

st.divider()

# ------------- Gráficos -------------
if df.empty:
    st.info("Nenhum dado para o período/filtros selecionados.")
else:
    # Por status
    by_status = df["status"].value_counts().reset_index()
    by_status.columns = ["status", "qtd"]
    fig1 = px.bar(by_status, x="status", y="qtd", title="Chamados por Status", text="qtd")
    fig1.update_layout(xaxis_title="", yaxis_title="Quantidade", uniformtext_minsize=10, uniformtext_mode="hide")
    st.plotly_chart(fig1, use_container_width=True)

    # Por dia
    if "criado_em" in df.columns:
        daily = df.set_index("criado_em").resample("D").size().rename("qtd").reset_index()
        fig2 = px.line(daily, x="criado_em", y="qtd", markers=True, title="Chamados por Dia")
        fig2.update_layout(xaxis_title="Data", yaxis_title="Quantidade")
        st.plotly_chart(fig2, use_container_width=True)

    # Top clientes
    if "cliente" in df.columns:
        top_clientes = df["cliente"].value_counts().head(10).reset_index()
        top_clientes.columns = ["cliente", "qtd"]
        fig3 = px.bar(top_clientes, x="cliente", y="qtd", title="Top 10 Clientes", text="qtd")
        fig3.update_layout(xaxis_title="", yaxis_title="Quantidade")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Tabela")
    st.dataframe(df.sort_values("criado_em", ascending=False) if "criado_em" in df.columns else df, use_container_width=True, height=420)

    # Export
    st.download_button(
        "⬇️ Baixar CSV filtrado",
        data=to_csv_download(df),
        file_name="chamados_filtrado.csv",
        mime="text/csv"
    )

st.caption("Dica: ajuste o tema em `.streamlit/config.toml` e personalize sua logo no cabeçalho se desejar.")
