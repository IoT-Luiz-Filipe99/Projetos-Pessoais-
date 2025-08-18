# 🤖 Automação de Atendimento (n8n + WhatsApp + Supabase)

Fluxo n8n pronto: **Webhook → Modelo Supabase → Render → Envio Zap → Log** com retry/erros.

## 🚀 Passo a passo
1. **Supabase**
   - Execute `supabase_schema.sql`.
   - Cadastre contatos e ajuste os modelos (placeholders `{{chave}}`).

2. **n8n**
   - Importar `n8n_workflow_automacao.json`.
   - Criar **Credentials**:
     - Supabase (REST) → URL do projeto + Anon/Service Key.
     - HTTP (Zap) → `ZAP_TOKEN` (Bearer).
   - Setar **Environment Variables** (Settings do n8n):
     - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ZAP_BASE_URL`, `ZAP_TOKEN`, `DEFAULT_TEMPLATE`.
   - Ativar o workflow e copiar a URL do **Webhook**.

3. **Teste**
   ```bash
   curl -X POST "https://SEU_N8N/webhook/whatsapp/notify" \
     -H "Content-Type: application/json" \
     -d '{"telefone":"5567999999999","modelo":"confirmacao_agendamento","variaveis":{"nome":"Erik","data":"18/08/2025","hora":"14:00"}}'
