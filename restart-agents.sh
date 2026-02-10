#!/bin/bash
# Script to restart all agent servers with updated code

echo "🔄 Restarting all agent servers..."

# Function to kill process on a port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ -n "$pid" ]; then
        echo "  Stopping server on port $port (PID: $pid)"
        kill $pid 2>/dev/null || true
        sleep 1
    fi
}

# Kill all running servers
echo "📦 Stopping old servers..."
kill_port 3978  # Python echo-m365
kill_port 3979  # .NET echo-m365
kill_port 3980  # TypeScript echo-m365
kill_port 3981  # .NET basic-m365
kill_port 3982  # Python basic-m365
kill_port 3983  # TypeScript basic-m365
kill_port 3984  # .NET emoji-chat
kill_port 3985  # Python emoji-chat
kill_port 3986  # TypeScript emoji-chat

echo ""
echo "✅ All servers stopped."
echo ""
echo "To start servers, run:"
echo "  TypeScript: cd typescript/samples/agents/echo-m365 && npm run build && npm start"
echo "  Python: cd python/samples/agents/echo-m365 && python3 -m src.start_server"
echo "  .NET: cd dotnet/samples/agents/EchoM365 && dotnet run"
echo ""
echo "Or use the start_samples.py script: python3 scripts/ci/start_samples.py echo-m365 --lang typescript"
