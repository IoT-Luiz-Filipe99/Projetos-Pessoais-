import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import time

st.set_page_config(page_title="Dashboard de Projetos", layout="wide")

# === Conexão com Supabase ===
url = "https://sowucbholfrgcyylwwad.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvd3VjYmhvbGZyZ2N5eWx3d2FkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDQ0NjAxNywiZXhwIjoyMDY2MDIyMDE3fQ.KZeAumGBXRsh__bulCp63Uco9uvAM3TNn6mtd2UI_wE"
supabase = create_client(url, key)

# === Função que carrega e trata os dados ===
@st.cache_data(ttl=60)
def carregar_dados():
    hist_diario = supabase.table("historico_diario").select("*").execute()
    df = pd.DataFrame(hist_diario.data)
    df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
    df["projeto"] = df["projeto"].str.strip()
    df["status"] = df["status"].str.strip()

    status_map = {
        "Pendente Agendamento": "Pendente",
        "Agendado": "Agendado",
        "Prospectar Técnico": "Prospectar",
        "Em Campo": "Em campo",
        "Finalizado": "Finalizado",
        "Cancelado": "Cancelado"
    }
    df["status_dashboard"] = df["status"].map(status_map)
    return df

# === Chamada dos dados ===
df_dia = carregar_dados()

# === Tabelas auxiliares ===
status_list = ['Pendente', 'Agendado', 'Prospectar', 'Em campo', 'Finalizado', 'Cancelado']
status_cores = {
    'Pendente': '#e74c3c',
    'Agendado': '#f1c40f',
    'Prospectar': '#e67e22',
    'Em campo': '#3498db',
    'Finalizado': '#2ecc71',
    'Cancelado': '#9b59b6'
}

# === Gera totais por projeto + status ===
valores_por_projeto_status = (
    df_dia.groupby(["projeto", "status_dashboard"])["total_cards"]
    .sum().unstack(fill_value=0).to_dict(orient="index")
)

# === Gera totais gerais (todos os projetos) ===
totais_gerais = (
    df_dia.groupby("status_dashboard")["total_cards"]
    .sum().reindex(status_list, fill_value=0).to_dict()
)

# === Estilo externo ===
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.header("⚙️ Filtros de Projetos")
    projetos_lista = list(valores_por_projeto_status.keys())
    projetos_selecionados = st.multiselect(
        "Selecione os projetos que deseja visualizar:",
        projetos_lista,
        default=projetos_lista
    )

# === Cabeçalho ===
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 style="margin-bottom:0;">🚀 Dashboard de Projetos</h1>
        <p style="margin-top:0;">Monitoramento em Tempo Real</p>
    </div>
    <div style="text-align: right;">
        <h3 style="color:#00FF00;">🟢 ONLINE</h3>
        <p>{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# === 📊 Visão Geral dos Projetos ===
st.subheader("📊 Visão Geral dos Projetos")
cols = st.columns(len(status_list))
for col, status in zip(cols, status_list):
    valor = totais_gerais.get(status, 0)
    col.markdown(f"""
    <div class="card-status">
        <div class="dot" style="color:{status_cores[status]}">●</div>
        <div class="value">{valor}</div>
        <div class="label">{status}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# === Cards por Projeto ===
if not projetos_selecionados:
    st.warning("⚠️ Nenhum projeto selecionado. Abra a barra lateral e selecione ao menos um.")
else:
    for projeto in projetos_selecionados:
        totais = valores_por_projeto_status.get(projeto, {})
        total_cards = sum(totais.get(status, 0) for status in status_list)
        st.subheader(f"📦 {projeto} - {total_cards} cards")
        cols = st.columns(6)
        for col, status in zip(cols, status_list):
            valor = totais.get(status, 0)
            col.markdown(f"""
            <div class="card-status">
                <div class="dot" style="color:{status_cores[status]}">●</div>
                <div class="value">{valor}</div>
                <div class="label">{status}</div>
            </div>
            """, unsafe_allow_html=True)



# === Atualização silenciosa automática ===
time.sleep(60)
st.rerun()

