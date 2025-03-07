#!/bin/bash

WORKDIR=$(dirname "$0")
LOGFILE="$WORKDIR/log_cron.txt"

MAX_LOG_SIZE=1048576  # 1MB em bytes

# Verifica se o log existe e seu tamanho
if [ -f "$LOGFILE" ]; then
    filesize=$(stat -c%s "$LOGFILE")
    if [ "$filesize" -gt "$MAX_LOG_SIZE" ]; then
        # Opcional: você pode mover o log para um backup e criar um novo
        rm "$LOGFILE" 
        touch "$LOGFILE"
    fi
fi

echo "Executando script em $(date)" >> "$LOGFILE"
cd "$WORKDIR" || { echo "Erro ao entrar no diretório" >> "$LOGFILE"; exit 1; }

# Ativa o ambiente virtual
source "$WORKDIR/.venv/bin/activate"
python -m uv run --env-file "$WORKDIR/.env" main.py"

echo "Finalizado em $(date)" >> "$LOGFILE"