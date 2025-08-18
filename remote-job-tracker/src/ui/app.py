from __future__ import annotations
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from src.match.rank import compute_match

st.set_page_config(page_title="Remote Job Tracker", page_icon="🌍", layout="wide")

DB_PATH = Path(__file__).resolve().parents[2] / "jobs.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

st.title("🌍 Remote Job Tracker")
st.caption("Filtre vagas remotas, ranqueie por match e salve favoritas.")

with st.sidebar:
    skills = st.text_area("Suas skills (separe por vírgulas)", "python, fastapi, streamlit, sql, pandas")
    company = st.text_input("Filtrar por empresa (opcional)")
    query = st.text_input("Busca livre (título/descrição)")
    top_k = st.slider("Top K por match", 10, 200, 50, 10)
    if st.button("Recarregar dados"):
        st.cache_data.clear()

@st.cache_data(show_spinner=False)
def load_jobs() -> pd.DataFrame:
    with engine.begin() as conn:
        df = pd.read_sql("select * from jobs order by id desc", conn)
    return df

df = load_jobs()
if query:
    df = df[df["title"].str.contains(query, case=False, na=False) | df["description"].str.contains(query, case=False, na=False)]
if company:
    df = df[df["company"].str.contains(company, case=False, na=False)]

if df.empty:
    st.info("Sem vagas no banco. Rode o ETL primeiro.")
    st.stop()

ranked = compute_match(df, skills, top_k=top_k)
st.subheader("Resultados ranqueados")
st.dataframe(ranked[["match","title","company","location","salary","url"]].style.format({"match":"{:.2f}"}), use_container_width=True, height=500)

sel = st.multiselect("Selecione IDs para salvar", ranked["id"].tolist())
note = st.text_input("Nota (opcional) para salvar")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Salvar selecionados"):
        if not sel:
            st.warning("Selecione pelo menos 1 vaga.")
        else:
            with engine.begin() as conn:
                for jid in sel:
                    conn.execute(text("insert into saved_jobs(job_id, note) values (:i, :n)"), {"i": int(jid), "n": note})
            st.success(f"{len(sel)} vagas salvas.")
with col2:
    csv = ranked.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV", data=csv, file_name="ranked_jobs.csv", mime="text/csv")
with col3:
    st.write("")

st.subheader("Favoritas")
with engine.begin() as conn:
    fav = pd.read_sql("""
        select s.id as saved_id, j.*
        from saved_jobs s join jobs j on j.id = s.job_id
        order by s.id desc
    """, conn)
st.dataframe(fav[["saved_id","title","company","location","url","salary"]], use_container_width=True, height=300)
