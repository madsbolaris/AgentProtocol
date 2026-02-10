#!/bin/bash
export PYTHONPATH=/Users/mabolan/AgentProtocol/python/microsoft-agents-protocol:$PYTHONPATH
export PORT=3978
cd /Users/mabolan/AgentProtocol/python/samples/agents/echo-m365
exec python3 -m src.main
