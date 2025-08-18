from __future__ import annotations
import os
from typing import Optional
import pandas as pd

try:
    from supabase import create_client, Client
except Exception:
    Client = None  # type: ignore

def get_supabase_client() -> Optional["Client"]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key or Client is None:
        return None
    return create_client(url, key)

def fetch_chamados_df(table: str, days: int = 7) -> pd.DataFrame:
    """
    Espera tabela com colunas (sugestão):
    id, cliente, cidade, uf, status, criado_em (timestamp), valor, categoria
    """
    client = get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase não configurado. Defina SUPABASE_URL e SUPABASE_ANON_KEY.")

    # Filtro de data (últimos 'days')
    from datetime import datetime, timedelta, timezone
    dt_from = datetime.now(timezone.utc) - timedelta(days=days)
    iso_from = dt_from.isoformat()

    # Query básica
    resp = client.table(table).select("*").gte("criado_em", iso_from).limit(5000).execute()
    data = resp.data or []
    df = pd.DataFrame(data)
    if df.empty:
        # Garante colunas mínimas
        df = pd.DataFrame(columns=["id","cliente","cidade","uf","status","criado_em","valor","categoria"])
    # Converte tipos
    if "criado_em" in df.columns:
        df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce")
    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df
