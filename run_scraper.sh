#!/bin/bash

# diretório onde o script está
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# diretório e arquivo de log
LOG_DIR="$SCRIPT_DIR/logs"
LOGFILE="$LOG_DIR/crontask.log"

# cria a pasta de logs se não existir
mkdir -p "$LOG_DIR"

# limite do log em bytes (1MB)
MAX_LOG_SIZE=$((1 * 1024 * 1024))

# verifica se o log existe e tamanho
if [ -f "$LOGFILE" ]; then
    filesize=$(stat -c%s "$LOGFILE")
    if [ "$filesize" -gt "$MAX_LOG_SIZE" ]; then
        # opcional: rotaciona para backup
        mv "$LOGFILE" "$LOGFILE.$(date +%Y%m%d%H%M%S).bak"
        touch "$LOGFILE"
    fi
fi

# log de execução
{
    echo "Executando script em $(date)"
    cd "$SCRIPT_DIR" || { echo "Erro ao entrar no diretório $SCRIPT_DIR"; exit 1; }

    source "./.venv/bin/activate"
    python -m uv run ./main.py

    echo "Finalizado em $(date)"
    echo "----------------------------"
} >> "$LOGFILE" 2>&1
