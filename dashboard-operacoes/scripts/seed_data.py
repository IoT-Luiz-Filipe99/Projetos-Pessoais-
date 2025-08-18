from __future__ import annotations
import os
import random
from datetime import datetime, timedelta, timezone
import pandas as pd

random.seed(42)

OUT_PATH = os.getenv("FAKE_CSV_PATH", "./scripts/fake_chamados.csv")
N = 500
statuses = ["Agendado", "Em campo", "Finalizado", "Cancelado", "Pendente"]
ufs = ["SP","RJ","MG","RS","SC","PR","BA","GO","MS","ES"]
clientes = [
    "AMERICANAS","DELFIA-TELMEX","FUST-CLARO-MS","MULT-PROJETOS","CLARO GO","CLARO PR",
    "TJMG - Fórum","TJMG - JESP","Galiléia","Paraguaçu","Viçosa","Passos","Contagem"
]
categorias = ["Manutenção","Instalação","Vistoria","Retorno Infra"]

now = datetime.now(timezone.utc)
rows = []
for i in range(1, N+1):
    dt = now - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    row = {
        "id": i,
        "cliente": random.choice(clientes),
        "cidade": random.choice(["Belo Horizonte","São Paulo","Rio de Janeiro","Campo Grande","Porto Alegre","Curitiba","Vitória","Goiânia"]),
        "uf": random.choice(ufs),
        "status": random.choices(statuses, weights=[25,20,35,5,15], k=1)[0],
        "criado_em": dt.isoformat(),
        "valor": round(random.uniform(80, 1800), 2),
        "categoria": random.choice(categorias),
    }
    rows.append(row)

df = pd.DataFrame(rows)
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
df.to_csv(OUT_PATH, index=False, encoding="utf-8")
print(f"[ok] CSV gerado em: {OUT_PATH} ({len(df)} linhas)")
