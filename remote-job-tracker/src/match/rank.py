"""
Funções de ranking por similaridade TF-IDF entre skills do usuário e a descrição/título da vaga.
"""
from __future__ import annotations
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_match(df: pd.DataFrame, skills: str, top_k: int = 50) -> pd.DataFrame:
    if df.empty:
        return df
    corpus = (df["title"].fillna("") + " " + df["description"].fillna("")).tolist()
    vec = TfidfVectorizer(stop_words="english", max_features=10000)
    X = vec.fit_transform(corpus)
    q = vec.transform([skills])
    sims = cosine_similarity(q, X).flatten()
    out = df.copy()
    out["match"] = (sims * 100).round(2)  # 0..100
    out = out.sort_values("match", ascending=False)
    return out.head(top_k).reset_index(drop=True)
