#!/bin/bash

WORKDIR="/home/berndof/Workspace/scraper"
LOGFILE="${WORKDIR}/cron_debug.log"


echo "Executando script em $(date)" >> "$LOGFILE"
cd "$WORKDIR" || { echo "Erro ao entrar no diretório" >> "$LOGFILE"; exit 1; }

#activate venv
source "$WORKDIR/.venv/bin/activate"
python -m uv run --env-file "$WORKDIR/.env" main.py

echo "Finalizado em $(date)" >> "$LOGFILE"