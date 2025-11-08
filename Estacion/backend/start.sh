#!/bin/bash

echo " Iniciando servicios de Estación..."

CONTAINER_IP=$(hostname -i)
echo " IP del contenedor: $CONTAINER_IP"

echo " Iniciando FastAPI + TCP Server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!
echo " FastAPI iniciado con PID: $FASTAPI_PID"

sleep 3

echo " Iniciando WebSocket bridge..."
node tcp_bridge.js