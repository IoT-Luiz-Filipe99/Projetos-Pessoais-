-- Contatos (dados mínimos)
create table if not exists public.contatos (
  id bigserial primary key,
  nome text not null,
  telefone text not null,             -- no formato internacional ex: 55DDDNUMERO
  cliente text,
  tags text[],
  ativo boolean default true
);

-- Modelos de mensagem (placeholders com {{chaves}})
create table if not exists public.modelos (
  id bigserial primary key,
  codigo text unique not null,        -- ex: 'confirmacao_agendamento'
  texto text not null,                -- ex: 'Olá {{nome}}, seu agendamento para {{data}} às {{hora}} está confirmado.'
  canal text default 'whatsapp'       -- futuro: sms/email
);

-- Logs de envio
create table if not exists public.envios_log (
  id bigserial primary key,
  telefone text not null,
  modelo text not null,
  payload jsonb not null,
  resposta jsonb,
  status text not null,               -- 'enviado','erro'
  criado_em timestamptz default now()
);

-- Modelo padrão
insert into public.modelos (codigo, texto) values
('confirmacao_agendamento', 'Olá {{nome}}, seu agendamento para {{data}} às {{hora}} está confirmado. Qualquer dúvida, responda este WhatsApp.'),
('lembrete_agendamento', 'Lembrete: amanhã {{data}} às {{hora}}. Endereço: {{endereco}}. Até lá, {{nome}}!')
on conflict do nothing;
