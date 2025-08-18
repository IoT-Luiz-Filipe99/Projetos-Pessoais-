import streamlit as st
import pandas as pd
import base64
from supabase import create_client
from datetime import date

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(layout="wide", page_title="Dashboard Futura Tecnologia")

# === CONTROLE DE TEMA ===
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# === CSS DINÂMICO E CLASSE DARK NO BODY ===
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

dark_class = "dark" if st.session_state.dark_mode else ""
st.markdown(f"<script>document.body.classList.add('{dark_class}');</script>", unsafe_allow_html=True)

# === CONEXÃO COM SUPABASE ===
projetos = [
    "AMERICANAS", "DELFIA-TELMEX", "FUST-CLARO-MS", "FUST-CLARO-RJ", "MULT-PROJETOS",
    "Projeto 1", "Projeto 2", "Projeto 3", "Projeto 4", "Projeto 5",
    "Projeto 6", "Projeto 7", "Projeto 8", "Projeto 9", "Projeto 10"
]

url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODk5NzgyNSwiZXhwIjoyMDY0NTczODI1fQ.TjwW4ztaD6CwFIDOK8aKm10VcgRvUZasMbst7Yiq3h0"
supabase = create_client(url, key)

# === CARREGAMENTO DOS DADOS ===
dfs = []
for nome in projetos:
    data = supabase.table(nome).select("*").execute().data
    df = pd.DataFrame(data)
    df["Cliente"] = nome
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)
df = df[df["Agendado"] != "Agendado"]

# === TRATAMENTO DE DATAS ===
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="%Y-%m-%d")
    df = df.dropna(subset=["Date"])
    df = df[df["Date"].dt.date <= date.today()]
    df["Date"] = df["Date"].dt.date

# === CONVERSÃO DE NÚMEROS ===
colunas_numericas = [
    "Agendado", "agendado para hoje", "Em Campo", "finalizado",
    "Prospectar Técnico", "Valores", "pendente agendamento", "id",
    "total pago hoje - dos chamados de hoje", "valor a pagar - finalizados hoje",
    "valor a pagar total", "pagamento a vista total", "pagamento a prazo total",
    "valor pago a vista", "valor pago do a prazo"
]
for col in colunas_numericas:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"R\\$", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# === COMPLETAR DADOS FALTANTES ===
for nome in projetos:
    if nome not in df["Cliente"].unique():
        df = pd.concat([df, pd.DataFrame([{
            "Cliente": nome,
            "Date": pd.to_datetime("today").date(),
            "pagamento a vista total": 0,
            "pagamento a prazo total": 0,
            "valor a pagar total": 0,
            "valor pago a vista": 0,
            "valor pago do a prazo": 0,
            "total pago hoje - dos chamados de hoje": 0
        }])], ignore_index=True)

# === SIDEBAR ===
with st.sidebar:
    datas_disponiveis = sorted(df["Date"].dropna().unique())
    data_selecionada = st.date_input(
        "📅 Selecione uma data:",
        value=max(datas_disponiveis),
        min_value=min(datas_disponiveis),
        max_value=max(datas_disponiveis)
    )
    st.markdown("---")
    projetos_selecionados = st.multiselect(
        "📦 Selecione os projetos:",
        options=projetos,
        default=projetos
    )

# === CABEÇALHO ===
# === CARDS RESUMO GERAL COM SOMATÓRIOS ===
df_filtrado = df[(df["Cliente"].isin(projetos_selecionados)) & (df["Date"] == data_selecionada)]

valor_pago_vista = df_filtrado["valor pago a vista"].sum()
valor_pago_prazo = df_filtrado["valor pago do a prazo"].sum()

resumo = {
    "🔹 A pagar à vista": df_filtrado["pagamento a vista total"].sum(),
    "🔸 A pagar a prazo": df_filtrado["pagamento a prazo total"].sum(),
    "📅 Total a pagar hoje": df_filtrado["valor a pagar total"].sum(),
    "✅ Pago à vista": valor_pago_vista,
    "🕓 Pago a prazo": valor_pago_prazo,
    "💰 Total pago hoje": valor_pago_vista + valor_pago_prazo  # ✅ Correto agora!
}


st.markdown("## 📊 Resumo Geral dos Projetos Selecionados")
colunas_resumo = st.columns(6)
for col, (titulo, valor) in zip(colunas_resumo, resumo.items()):
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <strong>{titulo}</strong><br>
                <span style="font-size: 1.5em;">R$ {valor:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)


# === CARDS COM TEXTO (sem ícones) ===
projetos_filtrados = [p for p in projetos if p in projetos_selecionados]
for i in range(0, len(projetos_filtrados), 5):
    linha = projetos_filtrados[i:i+5]
    cols = st.columns(len(linha))

    for col, projeto in zip(cols, linha):
        df_projeto = df[(df["Cliente"] == projeto) & (df["Date"] == data_selecionada)]

        pagamento_vista_total = float(df_projeto["pagamento a vista total"].sum() or 0)
        pagamento_prazo_total = float(df_projeto["pagamento a prazo total"].sum() or 0)
        total_a_pagar_hoje = float(df_projeto["valor a pagar total"].sum() or 0)
        pago_vista = float(df_projeto["valor pago a vista"].sum() or 0)
        pago_prazo = float(df_projeto["valor pago do a prazo"].sum() or 0)
        pago_total = pago_vista + pago_prazo

        with col:
            st.markdown(f"### {projeto}")
            st.markdown(f"""
                    <div class="metric-card">
                    <strong>🔹 A pagar à vista:</strong><br> R$ {pagamento_vista_total:,.2f}<br><br>
                    <strong>🔸 A pagar a prazo:</strong><br> R$ {pagamento_prazo_total:,.2f}<br><br>
                    <strong>📅 Total a pagar hoje:</strong><br> R$ {total_a_pagar_hoje:,.2f}<br><br>
                    <strong>✅ Pago à vista:</strong><br> R$ {pago_vista:,.2f}<br><br>
                    <strong>🕓 Pago a prazo:</strong><br> R$ {pago_prazo:,.2f}<br><br>
                    <strong>💰 Total pago hoje:</strong><br> R$ {pago_total:,.2f}
                </div>
                """, unsafe_allow_html=True)


