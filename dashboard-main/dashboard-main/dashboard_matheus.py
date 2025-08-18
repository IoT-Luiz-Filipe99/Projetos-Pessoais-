import pandas as pd 
import streamlit as st
import plotly.express as px
from supabase import create_client
#from fastapi import FastAPI, Request
#import uvicorn kk


st.set_page_config(layout="wide")
url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODk5NzgyNSwiZXhwIjoyMDY0NTczODI1fQ.TjwW4ztaD6CwFIDOK8aKm10VcgRvUZasMbst7Yiq3h0"
supabase = create_client(url, key)

@st.cache_data(ttl=60)  # cache com validade de 60 segundos
def carregar_dados():
    americanas = supabase.table("AMERICANAS").select("*").execute()
    del_tel = supabase.table("DELFIA-TELMEX").select("*").execute()
    fus_cla_ms = supabase.table("FUST-CLARO-MS").select("*").execute()
    fus_cla_rj = supabase.table("FUST-CLARO-RJ").select("*").execute()
    mul_pro = supabase.table("MULT-PROJETOS").select("*").execute()

    # Convertendo para DataFrames
    df_americanas = pd.DataFrame(americanas.data)
    df_del_tel = pd.DataFrame(del_tel.data)
    df_fus_cla_ms = pd.DataFrame(fus_cla_ms.data)
    df_fus_cla_rj = pd.DataFrame(fus_cla_rj.data)
    df_mul_pro = pd.DataFrame(mul_pro.data)

    # Adiciona coluna "Cliente"
    df_americanas["Cliente"] = "AMERICANAS"
    df_del_tel["Cliente"] = "DELFIA-TELMEX"
    df_fus_cla_ms["Cliente"] = "FUST-CLARO-MS"
    df_fus_cla_rj["Cliente"] = "FUST-CLARO-RJ"
    df_mul_pro["Cliente"] = "MULT-PROJETOS"

    # Junta tudo
    df = pd.concat([df_americanas, df_del_tel, df_fus_cla_ms, df_fus_cla_rj, df_mul_pro], ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    df["Dias"] = df["Date"].apply(lambda x: f"{x.year}-{x.month}-{x.day}")
    df = df.sort_values("Date")
    
    return df

df = carregar_dados()
dias = st.sidebar.selectbox("dias", df["Dias"].unique())
df_filtered = df[df["Dias"] == dias]


col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

fig_ag = px.bar(
    df_filtered,
    x="Cliente",
    y="Agendado",
    color="Cliente",
    title=f"Agendado por Cliente em {dias}",
    text="Agendado"
    
)
  # Aumenta o tamanho
col1.plotly_chart(fig_ag, use_container_width=True) 

fig_can = px.bar(
    df_filtered,
    x="Cliente",
    y="Cancelado",
    color="Cliente",
    title=f"Cancelado por Cliente em {dias}",
    text="Cancelado",
    orientation="v"
)
col2.plotly_chart(fig_can, use_container_width=True)

fig_ec = px.bar(
    df_filtered,
    x="Cliente",
    y="Em Campo",
    color="Cliente",
    title=f"Em Campo por Cliente em {dias}",
    text="Em Campo",
    
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