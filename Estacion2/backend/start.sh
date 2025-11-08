#!/bin/bash

echo "ðŸš€ Iniciando servicios de EstaciÃ³n..."

# Mostrar IP del contenedor
CONTAINER_IP=$(hostname -i)
echo "ðŸ“ IP del contenedor: $CONTAINER_IP"

# Iniciar FastAPI (incluye TCP server) en background
echo "ðŸ Iniciando FastAPI + TCP Server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!
echo "âœ… FastAPI iniciado con PID: $FASTAPI_PID"

# Dar tiempo al TCP server de Python para iniciar
sleep 3

# Iniciar el bridge Node.js (este se mantiene en foreground)
echo "ðŸŒ Iniciando WebSocket bridge..."
node tcp_bridge.js
