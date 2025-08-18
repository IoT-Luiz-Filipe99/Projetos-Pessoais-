#!/usr/bin/env bash
set -e

# Executa o pipeline completo (pode ser agendado no cron ou GitHub Actions)
python -m src.etl.extract_remoteok
python -m src.etl.normalize
python -m src.etl.load
echo "[ok] Pipeline diário concluído."
