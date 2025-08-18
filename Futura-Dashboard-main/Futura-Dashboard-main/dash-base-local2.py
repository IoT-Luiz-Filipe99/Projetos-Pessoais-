import pandas as pd 
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# Lê todas as abas
df_abas = pd.read_excel('banco_dados.xlsx', sheet_name=None)

# Junta tudo num único DataFrame e adiciona coluna 'Cliente'
dados_completos = []
for nome, aba in df_abas.items():
    temp = aba.copy()
    temp["Cliente"] = nome  
    dados_completos.append(temp)

df = pd.concat(dados_completos)

# Trata a coluna Dia
df["Dia"] = pd.to_datetime(df["Dia"], dayfirst=True, errors='coerce')
df = df.dropna(subset=["Dia"])
df["Dias"] = df["Dia"].dt.strftime("%Y-%m-%d")

# Cria o filtro lateral
dias = st.sidebar.selectbox("Dia", df["Dias"].unique())
df_filtered = df[df["Dias"] == dias]

# Mostra os dados
st.subheader(f"Dados do dia {dias}")
st.dataframe(df_filtered)

# Gráfico de barras empilhadas por cliente
st.subheader("Gráfico por Cliente")
fig = px.bar(
    df_filtered,
    x="Cliente",
    y=["Agendado", "Cancelado", "Em Campo", "Aguardando Equipamento", "Prospectar Técnico"],
    title=f"Status por Cliente - {dias}",
    barmode="stack"
)
st.plotly_chart(fig, use_container_width=True)
