import pandas as pd 
import streamlit as st
import plotly.express as px
from supabase import create_client

url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODk5NzgyNSwiZXhwIjoyMDY0NTczODI1fQ.TjwW4ztaD6CwFIDOK8aKm10VcgRvUZasMbst7Yiq3h0"
supabase = create_client(url, key)

americanas = supabase.table("AMERICANAS").select("*").execute()
del_tel = supabase.table("DELFIA-TELMEX").select("*").execute()
fus_cla_ms = supabase.table("FUST-CLARO-MS").select("*").execute()
fus_cla_rj = supabase.table("FUST-CLARO-RJ").select("*").execute()
mul_pro = supabase.table("MULT-PROJETOS").select("*").execute()

#------------------------------------------------------#
dados_americanas = americanas.data
df_americanas = pd.DataFrame(dados_americanas)    #AMERICANAS
print(df_americanas.head())
#------------------------------------------------------#
dados_del_tel = del_tel.data
df_del_tel = pd.DataFrame(dados_del_tel)          #DELFIA-TELMEX
print(df_del_tel.head())
#------------------------------------------------------#
dados_fus_cla_ms = fus_cla_ms.data
df_fus_cla_ms = pd.DataFrame(dados_fus_cla_ms)          #FUST-CLARO-MS
print(df_fus_cla_ms.head())
#------------------------------------------------------#
dados_fus_cla_rj = fus_cla_rj.data
df_fus_cla_rj = pd.DataFrame(dados_fus_cla_rj)          #FUST-CLARO-RJ
print(df_fus_cla_rj.head())
#------------------------------------------------------#
dados_mul_pro = mul_pro.data
df_mul_pro = pd.DataFrame(dados_mul_pro)          #MULT-PROJETOS
print(df_mul_pro.head())
#------------------------------------------------------#

dfs = [df_americanas, df_del_tel, df_fus_cla_ms, df_fus_cla_rj, df_mul_pro]

df_americanas["Cliente"] = "AMERICANAS"
df_del_tel["Cliente"] = "DELFIA-TELMEX"
df_fus_cla_ms["Cliente"] = "FUST-CLARO-MS"
df_fus_cla_rj["Cliente"] = "FUST-CLARO-RJ"
df_mul_pro["Cliente"] = "MULT-PROJETOS"


# Concatena verticalmente (empilha as linhas)
df_unificado = pd.concat(dfs, ignore_index=True)


