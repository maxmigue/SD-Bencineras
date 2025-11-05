from fastapi import FastAPI
import asyncio
import subprocess
from tcp_server import iniciar_tcp_servidor

app = FastAPI(title="Backend Bencinera", version="1.0")

@app.on_event("startup")
async def iniciar_componentes():
    # 🔹 Iniciar el servidor TCP en paralelo
    asyncio.create_task(iniciar_tcp_servidor())
    print("🚀 Servidor TCP iniciado junto con FastAPI")

    # 🔹 (Opcional) Iniciar el bridge Node.js automáticamente
    try:
        subprocess.Popen(["node", "tcp_bridge.js"], cwd=".", shell=True)
        print("🌐 Bridge Node.js iniciado correctamente")
    except Exception as e:
        print("⚠️ No se pudo iniciar el bridge:", e)

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend FastAPI funcionando correctamente"}
