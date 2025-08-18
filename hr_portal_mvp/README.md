# Portal do Colaborador — MVP (Local)

Este projeto é um ponto de partida **do zero** para um site de RH & Comunicação com:

- Autenticação (cadastro/login)
- Comunicados internos
- Solicitação de férias
- Chat por departamento (tempo real, WebSocket)
- **Ponto mobile** com GPS + selfie
- Treinamentos com quiz + **certificado em PDF**
- Relatórios básicos do RH
- Upload e listagem de **holerites** (pasta do colaborador)

> Este MVP roda **localmente** com SQLite. Depois, podemos evoluir para **Supabase** (auth/DB/storage) e implantação em nuvem.

---

## Como rodar

1. **Instale o Python 3.10+**: https://www.python.org/downloads/
2. **Abra o terminal** e navegue até a pasta `backend` deste projeto.
3. Crie e ative um ambiente virtual:
   - Windows:
     ```bat
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
4. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
5. Inicie o servidor:
   ```bash
   uvicorn main:app --reload
   ```
6. Abra o navegador em: **http://127.0.0.1:8000**

> Frontend é servido em `/static`. Uploads/certificados/selfies ficam em `/uploads`.

### Acesso inicial

Usuário admin automático (criado no primeiro start):

- **E-mail:** `admin@corp.com`
- **Senha:** `admin123`
- **Departamento:** RH
- **Permissão:** admin

Você pode se cadastrar como colaborador em `/static/register.html`.

---

## Estrutura

```
/backend
  main.py              # FastAPI + WebSocket + SQLite + PDFs
  app.db               # (gerado na primeira execução)
  /../frontend         # arquivos estáticos servidos em /static
  /../uploads          # selfies, holerites, certificados
/frontend
  index.html, login.html, register.html, dashboard.html,
  timeclock.html, chat.html, training.html, reports.html,
  styles.css, utils.js
```

---

## Próximos passos (sugestão)

- **Supabase**: mover autenticação/DB/storage; Single Sign-On (Google/Microsoft)
- **Controle de ponto**: adicionar **check-out**, validação de perímetro (geofence) e justificativa
- **Fluxo de férias**: aprovações em cadeia, anexos e trilhas de auditoria
- **Relatórios RH**: gráficos (Chart.js), exportação CSV/XLSX
- **Permissões**: papéis (admin, gestor, colaborador)
- **Produção**: Deploy no **Railway/Fly.io/Render**, domínio e HTTPS
- **LGPD**: política de privacidade, retenção e consentimento de dados

---

## Segurança (MVP)

Este projeto é educativo. Em produção:
- Troque `SECRET_KEY` (variável de ambiente `APP_SECRET_KEY`).
- Use HTTPS (TLS), cookies **HttpOnly/SameSite** e rotação de tokens.
- Faça verificação robusta das imagens (ex.: antivírus/clamscan) e limites de tamanho.
- Proteja uploads com storage privado (ex.: Supabase Storage/S3).

Bom estudo e boa construção! 🚀