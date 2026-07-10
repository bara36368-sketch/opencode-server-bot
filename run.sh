#!/data/data/com.termux/files/usr/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
echo "[$(date)] run.sh started" >> run.log
while true; do
    if [ -f setenv.sh ]; then
        source setenv.sh
    else
        echo "[$(date)] setenv.sh not found!" >> run.log
    fi
    echo "[$(date)] Starting bot..." | tee -a run.log
    python opencode_bot.py >> run.log 2>&1
    EXIT_CODE=$?
    echo "[$(date)] Bot exited (code $EXIT_CODE)" >> run.log
    if [ -f maintenance.lock ]; then
        echo "[$(date)] Maintenance mode. Stopped." >> run.log
        rm -f maintenance.lock
        break
    fi
    sleep 2
done
