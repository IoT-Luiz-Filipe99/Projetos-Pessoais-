 
import streamlit as st

from datetime import datetime
 
st.set_page_config(page_title="Dashboard de Projetos", layout="wide")
 
# =========================

# Sidebar de Filtros

# =========================

with st.sidebar:

    st.header("⚙️ Filtros de Projetos")

    projetos_lista = ['Fust-Claro', 'Fusto-Vivo', 'Telmex', 'Americanas']

    projetos_selecionados = st.multiselect(

        "Selecione os projetos que deseja visualizar:",

        projetos_lista,

        default=projetos_lista  # Começa com todos selecionados

    )

    st.markdown("---")

    st.info("↖️ Clique na seta no topo para ocultar a barra!")
 
# =========================

# Cabeçalho

# =========================

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<h1 style="margin-bottom:0;">🚀 Dashboard de Projetos</h1>
<p style="margin-top:0;">Monitoramento em Tempo Real</p>
</div>
<div style="text-align: right;">
<h3 style="color:#00FF00;">🟢 ONLINE - 15 CARDS</h3>
<p>{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</p>
</div>
</div>

""", unsafe_allow_html=True)
 
st.markdown("---")
 
# =========================

# Dados Simulados

# =========================

status_list = ['Pendente', 'Agendado', 'Prospectar', 'Em', 'Finalizado', 'Cancelado']

status_cores = {

    'Pendente': '#f1c40f',

    'Agendado': '#3498db',

    'Prospectar': '#e67e22',

    'Em': '#9b59b6',

    'Finalizado': '#2ecc71',

    'Cancelado': '#e74c3c'

}
 
# Quantidade por status (exemplo)

totais = {'Pendente': 4, 'Agendado': 2, 'Prospectar': 2, 'Em': 3, 'Finalizado': 3, 'Cancelado': 1}
 
# =========================

# Cards de Visão Geral

# =========================

st.subheader("📊 Visão Geral dos Projetos")

cols = st.columns(len(status_list))

for col, status in zip(cols, status_list):

    col.markdown(f"""
<div style="background-color: #1e1e2f; padding: 20px; border-radius: 10px; text-align: center; color: white;">
<div style="font-size: 26px; color: {status_cores[status]};">●</div>
<h2 style="margin:0;">{totais[status]}</h2>
<p style="margin:0;">{status}</p>
</div>

    """, unsafe_allow_html=True)
 
st.markdown("---")
 
# =========================

# Cards por Projeto

# =========================

if not projetos_selecionados:

    st.warning("⚠️ Nenhum projeto selecionado. Abra a barra lateral e selecione ao menos um.")

else:

    for projeto in projetos_selecionados:

        st.subheader(f"📦 {projeto} - 4 cards")
 
        cols = st.columns(6)

        for col, status in zip(cols, status_list):

            col.markdown(f"""
<div style="background-color: #282846; padding: 15px; border-radius: 10px; text-align: center; color: white;">
<div style="font-size: 20px; color: {status_cores[status]};">●</div>
<h3 style="margin:0;">1</h3>
<p style="margin:0;">{status}</p>
</div>

            """, unsafe_allow_html=True)
 
st.markdown("---")
 
# =========================

# Alertas

# =========================

st.subheader("🚨 Alertas")

st.markdown("""
<div style="background-color: #3b2d3b; padding: 20px; border-radius: 10px;">
<div style="background-color: #5b3d5b; padding: 10px; border-radius: 8px; margin-bottom:10px;">
<strong style="color:red;">⚠️ Card AM003 há mais de 24h</strong> <span style="float:right; background-color:#777;padding:2px 6px;border-radius:4px;">Americanas</span>
</div>
<div style="background-color: #5b3d5b; padding: 10px; border-radius: 8px; margin-bottom:10px;">
<strong style="color:red;">⚠️ Card TX003 há mais de 24h</strong> <span style="float:right; background-color:#777;padding:2px 6px;border-radius:4px;">Telmex</span>
</div>
<div style="background-color: #5b3d5b; padding: 10px; border-radius: 8px;">
<strong style="color:red;">⚠️ Card FC003 há mais de 24h</strong> <span style="float:right; background-color:#777;padding:2px 6px;border-radius:4px;">Fust-Claro</span>
</div>
<p style="text-align: center; color:#bbb;">+8 alertas adicionais</p>
</div>

""", unsafe_allow_html=True)

 