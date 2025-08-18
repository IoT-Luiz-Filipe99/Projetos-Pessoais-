import pandas as pd 
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")


df_abas = pd.read_excel('banco_dados.xlsx', sheet_name=None)

dados_completos = []
for nome, aba in df_abas.items():
    temp = aba.copy()
    temp["Cliente"] = nome  
    dados_completos.append(temp)

df = pd.concat(dados_completos)

df["Date"] = pd.to_datetime(df["Date"])
df=df.sort_values("Date")
df["Dias"] = df["Date"].apply(lambda x: str(x.year) + "-" + str(x.month) + "-" + str(x.day))
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


#fig_dias = px.line(df, x="Date", y="Agendado", title='Life expectancy in Canada')
#col1.plotly_chart(fig_dias, use_container_width=True)