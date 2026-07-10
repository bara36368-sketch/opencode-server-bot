#!/data/data/com.termux/files/usr/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
while true; do
    source setenv.sh 2>/dev/null
    echo "[$(date)] Starting bot..."
    python opencode_bot.py
    EXIT_CODE=$?
    if [ -f maintenance.lock ]; then
        echo "[$(date)] Maintenance mode. Stopped."
        rm -f maintenance.lock
        break
    fi
    echo "[$(date)] Bot exited (code $EXIT_CODE). Restarting in 2s..."
    sleep 2
done
