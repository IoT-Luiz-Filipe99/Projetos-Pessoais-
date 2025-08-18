import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Dashboard de Projetos", layout="wide")
st.title("📊 Dashboard de Projetos")

# Simulação de dados (caso você ainda não tenha enviado uma planilha)
dados = {
    "Data": pd.date_range(start="2025-01-01", periods=6, freq="M"),
    "Projeto": ["A", "B", "C", "A", "B", "C"],
    "Status": ["Concluído", "Em Andamento", "Cancelado", "Em Andamento", "Concluído", "Cancelado"],
    "Valor": [1000, 1500, 1200, 1100, 1600, 900]
}
df = pd.DataFrame(dados)

# Filtros
st.sidebar.header("Filtros")
projetos = st.sidebar.multiselect("Projeto", df["Projeto"].unique())
status = st.sidebar.multiselect("Status", df["Status"].unique())

if projetos:
    df = df[df["Projeto"].isin(projetos)]
if status:
    df = df[df["Status"].isin(status)]

# KPIs
st.metric("💰 Valor Total", f"R$ {df['Valor'].sum():,.2f}")
st.metric("📈 Média por Projeto", f"R$ {df['Valor'].mean():,.2f}")

# Gráfico de barras
fig1 = px.bar(df, x="Projeto", y="Valor", color="Status", barmode="group", title="Valor por Projeto e Status")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico de linha
fig2 = px.line(df, x="Data", y="Valor", color="Projeto", title="Evolução dos Projetos")
st.plotly_chart(fig2, use_container_width=True)

# Tabela
st.subheader("📄 Dados Detalhados")
st.dataframe(df)
