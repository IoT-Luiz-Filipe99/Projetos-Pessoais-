import pandas as pd
from src.match.rank import compute_match

def test_compute_match_scores():
    df = pd.DataFrame([
        {"id":1, "title":"Python Dev", "description":"Build APIs with FastAPI"},
        {"id":2, "title":"Front-end React", "description":"React, UI/UX"},
    ])
    out = compute_match(df, "python, fastapi", top_k=2)
    assert "match" in out.columns
    assert out.iloc[0]["id"] == 1  # deve ranquear Python/FastAPI acima
