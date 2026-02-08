#!/bin/bash
# Start all echo bots on their configured ports
# Reads port configuration from echo-m365-ports.json at project root

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PORTS_FILE="$PROJECT_ROOT/echo-m365-ports.json"

# Check if ports file exists
if [ ! -f "$PORTS_FILE" ]; then
    echo "Error: echo-m365-ports.json not found at project root"
    exit 1
fi

# Read ports from JSON file
PYTHON_PORT=$(jq -r '.python' "$PORTS_FILE")
DOTNET_PORT=$(jq -r '.dotnet' "$PORTS_FILE")
TYPESCRIPT_PORT=$(jq -r '.typescript' "$PORTS_FILE")

echo "Starting echo bots with configured ports:"
echo "  Python: $PYTHON_PORT"
echo "  .NET: $DOTNET_PORT"
echo "  TypeScript: $TYPESCRIPT_PORT"
echo ""

# Create log directory
LOG_DIR="$PROJECT_ROOT/.logs"
mkdir -p "$LOG_DIR"

# Function to stop all echo bots on exit
cleanup() {
    echo ""
    echo "Stopping all echo bots..."
    kill $(jobs -p) 2>/dev/null || true
    wait
    echo "All echo bots stopped."
}
trap cleanup EXIT INT TERM

# Start Python echo bot
echo "Starting Python echo bot on port $PYTHON_PORT..."
cd "$PROJECT_ROOT/python/samples/agents/echo-m365"
PORT=$PYTHON_PORT python src/start_server.py > "$LOG_DIR/python-echo-m365.log" 2>&1 &
PYTHON_PID=$!
echo "  Python echo bot PID: $PYTHON_PID"

# Start .NET echo bot
echo "Starting .NET echo bot on port $DOTNET_PORT..."
cd "$PROJECT_ROOT/dotnet/samples/agents/EchoM365"
PORT=$DOTNET_PORT dotnet run > "$LOG_DIR/dotnet-echo-m365.log" 2>&1 &
DOTNET_PID=$!
echo "  .NET echo bot PID: $DOTNET_PID"

# Start TypeScript echo bot
echo "Starting TypeScript echo bot on port $TYPESCRIPT_PORT..."
cd "$PROJECT_ROOT/typescript/samples/echo-m365"
PORT=$TYPESCRIPT_PORT npm start > "$LOG_DIR/typescript-echo-m365.log" 2>&1 &
TYPESCRIPT_PID=$!
echo "  TypeScript echo bot PID: $TYPESCRIPT_PID"

echo ""
echo "All echo bots started successfully!"
echo "Logs are available in $LOG_DIR/"
echo ""
echo "To test the echo bots, use:"
echo "  curl -X POST http://localhost:$PYTHON_PORT/health"
echo "  curl -X POST http://localhost:$DOTNET_PORT/health"
echo "  curl -X POST http://localhost:$TYPESCRIPT_PORT/health"
echo ""
echo "Press Ctrl+C to stop all echo bots"
echo ""

# Wait for all background processes
wait
