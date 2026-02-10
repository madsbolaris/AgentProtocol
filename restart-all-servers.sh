#!/bin/bash

echo "========================================="
echo "Restarting All Basic M365 Servers"
echo "========================================="

# Kill all existing servers
echo "Stopping existing servers..."
ps aux | grep -E "(dotnet run|npm start|python.*main\.py)" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
sleep 3

# Start .NET server
echo "Starting .NET server..."
cd /Users/mabolan/AgentProtocol/dotnet/samples/agents/BasicM365Agent
dotnet run > /tmp/dotnet-basic-m365.log 2>&1 &
echo "  .NET started (PID: $!)"

# Start Python server
echo "Starting Python server..."
cd /Users/mabolan/AgentProtocol/python/samples/agents/basic-m365
USE_LLM_RECORDINGS=true python3 src/main.py > /tmp/python-basic-m365.log 2>&1 &
echo "  Python started (PID: $!)"

# Start TypeScript server
echo "Starting TypeScript server..."
cd /Users/mabolan/AgentProtocol/typescript/samples/agents/basic-m365
npm start > /tmp/typescript-basic-m365.log 2>&1 &
echo "  TypeScript started (PID: $!)"

echo ""
echo "Waiting for servers to start..."
sleep 15

echo ""
echo "========================================="
echo "Server Status"
echo "========================================="
lsof -ti :3981 > /dev/null && echo "✅ .NET running on :3981" || echo "❌ .NET not running"
lsof -ti :3982 > /dev/null && echo "✅ Python running on :3982" || echo "❌ Python not running"
lsof -ti :3983 > /dev/null && echo "✅ TypeScript running on :3983" || echo "❌ TypeScript not running"

echo ""
echo "========================================="
echo "Checking LLM Recording Status"
echo "========================================="
echo "=== Python log (first 20 lines) ==="
head -20 /tmp/python-basic-m365.log

echo ""
echo "Done!"
