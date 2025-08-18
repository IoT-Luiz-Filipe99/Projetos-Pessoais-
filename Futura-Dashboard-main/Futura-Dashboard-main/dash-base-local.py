import pandas as pd 
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

df_abas = pd.read_excel('banco_dados.xlsx', sheet_name=None)
americanas = df_abas['Amercanas']
mul_pro = df_abas['MULT-PROJETOS']
fus_cla_rj = df_abas['FUST-CLARO-RJ']
fus_cla_ms = df_abas['FUST-CLARO-MS']
del_tel = df_abas['DELFIA-TELMEX']

dados_completos = []
for nome, aba in df_abas.items():
    temp = aba.copy()
    temp["Cliente"] = nome  
    dados_completos.append(temp)

df = pd.concat(dados_completos)


