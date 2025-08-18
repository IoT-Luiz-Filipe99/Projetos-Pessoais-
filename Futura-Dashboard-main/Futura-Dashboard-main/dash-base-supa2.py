import pandas as pd 
import streamlit as st
import plotly.express as px
from supabase import create_client, Client

# Supabase configs
url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5OTc4MjUsImV4cCI6MjA2NDU3MzgyNX0.A34oFB-m_hTZ0Ar5Z-5l66IRDIxheyI3zBLIilruid4"
supabase: Client = create_client(url, key)

# Layout do Streamlit
st.set_page_config(layout="wide")

# Busca os dados do Supabase
response = supabase.table("Agendado").select("*").execute()
df = pd.DataFrame(response.data)

# Pré-processamento
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df["Dias"] = df["Date"].dt.strftime("%Y-%m-%d")

# Filtro lateral
dias = st.sidebar.selectbox("dias", df["Dias"].unique())
df_filtered = df[df["Dias"] == dias]

# Layout de colunas
col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

# Gráficos
fig_ag = px.bar(
    df_filtered,
    x="Cliente",
    y="Agendado",
    color="Cliente",
    title=f"Agendado por Cliente em {dias}",
    text="Agendado"
)
col1.plotly_chart(fig_ag, use_container_width=True)

fig_can = px.bar(
    df_filtered,
    x="Cliente",
    y="Cancelado",
    color="Cliente",
    title=f"Cancelado por Cliente em {dias}",
    text="Cancelado"
)
col2.plotly_chart(fig_can, use_container_width=True)

fig_ec = px.bar(
    df_filtered,
    x="Cliente",
    y="Em Campo",
    color="Cliente",
    title=f"Em Campo por Cliente em {dias}",
    text="Em Campo"
)
col3.plotly_chart(fig_ec, use_container_width=True)

fig_pt = px.bar(
    df_filtered,
    x="Cliente",
    y="Prospectar Técnico",
    color="Cliente",
    title=f"Prospectar Técnico por Cliente em {dias}",
    text="Prospectar Técnico"
)
col4.plotly_chart(fig_pt, use_container_width=True)

fig_ee = px.pie(
    df_filtered,
    values="Aguardando Equipamento",
    names="Cliente",
    title=f"Aguardando equipamento por Cliente em {dias}"
)
col5.plotly_chart(fig_ee, use_container_width=True)
