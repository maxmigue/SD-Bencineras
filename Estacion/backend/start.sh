#!/bin/bash

echo "🚀 Iniciando servicios de Estación..."

# Iniciar el bridge Node.js en background
echo "🌐 Iniciando WebSocket bridge..."
node tcp_bridge.js &
BRIDGE_PID=$!
echo "✅ Bridge iniciado con PID: $BRIDGE_PID"

# Dar tiempo al bridge para iniciar
sleep 2

# Iniciar FastAPI (incluye TCP server)
echo "🐍 Iniciando FastAPI + TCP Server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
