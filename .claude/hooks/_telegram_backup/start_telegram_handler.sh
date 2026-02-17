#!/bin/bash
# Start the Telegram Response Handler in the background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDLER="$SCRIPT_DIR/telegram_response_handler.py"
PID_FILE="/tmp/telegram_handler.pid"
LOG_FILE="/tmp/telegram_handler.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Handler already running (PID: $PID)"
        echo "   Use: $SCRIPT_DIR/stop_telegram_handler.sh to stop it first"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start the handler in the background
echo "🚀 Starting Telegram Response Handler..."
nohup python3 "$HANDLER" > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo "$PID" > "$PID_FILE"

echo "✅ Handler started (PID: $PID)"
echo "📝 Logs: tail -f $LOG_FILE"
echo "🛑 Stop: $SCRIPT_DIR/stop_telegram_handler.sh"
