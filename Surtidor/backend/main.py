from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import socket
import json
import random
import time

# --- Estado del Surtidor (simulando una base de datos en memoria) ---
surtidor = {
    "id": random.randint(1, 1000),
    "nombre": "Surtidor Delta",
    "estado": "Parado", # Parado, Cargando combustible, Fuera de servicio
    "tipo_combustible": "Gasolina 95",
    "precio_litro": 1350,
    "litros_despachados": 0.0,
    "total_cobrado": 0.0
}

# --- Configuración de FastAPI ---
app = FastAPI(
    title="API del Surtidor",
    description="Permite controlar y monitorear un surtidor simulado.",
    version="1.0.0"
)

# CORS para permitir que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # O idealmente, http://localhost:3001 para el frontend del surtidor
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cliente TCP para comunicarse con la Estación ---
HOST_ESTACION = "127.0.0.1"
PORT_ESTACION = 5000
writer = None

async def conectar_a_estacion():
    global writer
    while True:
        try:
            reader, writer = await asyncio.open_connection(HOST_ESTACION, PORT_ESTACION)
            print(f"✅ Conectado a la estación en {HOST_ESTACION}:{PORT_ESTACION}")
            # Enviar estado inicial al conectar
            await enviar_estado()
            # Mantener la conexión viva y escuchar por si la estación envía algo (aunque en este caso no lo hace)
            while not reader.at_eof():
                await reader.read(100) # Simplemente mantener la conexión abierta
        except (ConnectionRefusedError, OSError) as e:
            print(f"🔌 No se pudo conectar a la estación: {e}. Reintentando en 5 segundos...")
            writer = None
        except Exception as e:
            print(f"❌ Error inesperado en la conexión TCP: {e}")
            writer = None
        await asyncio.sleep(5)


async def enviar_estado():
    global writer
    if writer:
        try:
            # Adaptar el formato al que espera la estación
            estado_para_estacion = {
                "id": surtidor["id"],
                "nombre": surtidor["nombre"],
                "estado": surtidor["estado"],
                "precio_93": 1290, # Simulado, podría venir del estado
                "precio_95": surtidor["precio_litro"],
                "precio_97": 1400,
                "precio_diesel": 1120
            }
            data_a_enviar = (json.dumps(estado_para_estacion) + "\n").encode()
            writer.write(data_a_enviar)
            await writer.drain()
            print(f"📤 Estado enviado a la estación: {estado_para_estacion}")
        except Exception as e:
            print(f"❌ Error al enviar estado a la estación: {e}")
            # La conexión podría estar rota, el bucle principal intentará reconectar
            writer = None
    else:
        print("⚠️ No hay conexión con la estación para enviar el estado.")

# --- Simulación de carga de combustible ---
async def simular_carga():
    while True:
        if surtidor["estado"] == "Cargando combustible":
            await asyncio.sleep(1) # Carga 1 litro por segundo
            surtidor["litros_despachados"] += 1
            surtidor["total_cobrado"] = surtidor["litros_despachados"] * surtidor["precio_litro"]
            print(f"💧 Cargando... {surtidor['litros_despachados']:.1f} L - ${surtidor['total_cobrado']:.0f}")
            await enviar_estado() # Enviar actualización durante la carga
        await asyncio.sleep(1)


# --- Eventos de inicio de FastAPI ---
@app.on_event("startup")
async def startup_event():
    # Iniciar la conexión con la estación en segundo plano
    asyncio.create_task(conectar_a_estacion())
    # Iniciar la simulación de carga en segundo plano
    asyncio.create_task(simular_carga())


# --- Endpoints de la API ---
@app.get("/estado")
async def get_estado():
    """Obtiene el estado actual del surtidor."""
    return surtidor

@app.post("/control/iniciar-carga")
async def iniciar_carga():
    """Inicia la carga de combustible."""
    if surtidor["estado"] == "Parado":
        surtidor["estado"] = "Cargando combustible"
        surtidor["litros_despachados"] = 0.0
        surtidor["total_cobrado"] = 0.0
        await enviar_estado()
        return {"mensaje": "Carga iniciada"}
    raise HTTPException(status_code=400, detail="El surtidor no está parado.")

@app.post("/control/detener-carga")
async def detener_carga():
    """Detiene la carga de combustible."""
    if surtidor["estado"] == "Cargando combustible":
        surtidor["estado"] = "Parado"
        await enviar_estado()
        return {"mensaje": f"Carga detenida. Total: ${surtidor['total_cobrado']:.0f}"}
    raise HTTPException(status_code=400, detail="El surtidor no está cargando combustible.")

@app.put("/configuracion")
async def update_config(nombre: str, precio_litro: int):
    """Actualiza la configuración del surtidor."""
    surtidor["nombre"] = nombre
    surtidor["precio_litro"] = precio_litro
    await enviar_estado()
    return {"mensaje": "Configuración actualizada", "nuevo_estado": surtidor}
