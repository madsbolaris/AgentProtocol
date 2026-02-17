#!/bin/bash
# Stop the Telegram Response Handler

PID_FILE="/tmp/telegram_handler.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  Handler not running (no PID file found)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  Handler not running (PID $PID doesn't exist)"
    rm "$PID_FILE"
    exit 0
fi

echo "🛑 Stopping Telegram Response Handler (PID: $PID)..."
kill "$PID"

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Handler stopped"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 0.5
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  Process didn't stop gracefully, force killing..."
    kill -9 "$PID"
    sleep 0.5
fi

rm "$PID_FILE"
echo "✅ Handler stopped (forced)"
