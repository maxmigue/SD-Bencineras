from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
import time
import copy
from collections import deque

# --- Estado del Surtidor (simulando una base de datos en memoria) ---
surtidor = {
    "id": random.randint(1, 1000),
    "nombre": "Surtidor Delta",
    "estado": "Parado",  # Parado, Cargando combustible, Fuera de servicio
    "tipo_combustible": "Gasolina 95",
    "precio_litro": 1350,
    "litros_despachados": 0.0,
    "total_cobrado": 0.0
}

# --- Cola para eventos pendientes y configuración de FastAPI ---
eventos_pendientes = deque()
app = FastAPI(
    title="API del Surtidor",
    description="Permite controlar y monitorear un surtidor simulado.",
    version="1.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lógica de Conexión y Sincronización con la Estación ---
HOST_ESTACION = "127.0.0.1"
PORT_ESTACION = 5000

async def encolar_estado_actual():
    """Prepara el estado actual del surtidor y lo añade a la cola de eventos pendientes."""
    surtidor_copy = copy.deepcopy(surtidor)
    
    # Define la transacción/evento con todos los datos relevantes
    evento = {
        "id": surtidor_copy["id"],
        "nombre": surtidor_copy["nombre"],
        "estado": surtidor_copy["estado"],
        "litros_despachados": surtidor_copy.get("litros_despachados", 0),
        "total_cobrado": surtidor_copy.get("total_cobrado", 0),
        "tipo_combustible": surtidor_copy.get("tipo_combustible"),
        "timestamp": time.time(),
        # Datos adicionales que la estación podría necesitar
        "precio_93": 1290,
        "precio_95": surtidor_copy["precio_litro"],
        "precio_97": 1400,
        "precio_diesel": 1120,
    }
    eventos_pendientes.append(evento)
    print(f"📥 Evento encolado. Pendientes: {len(eventos_pendientes)}")

async def conectar_y_sincronizar():
    """
    Mantiene la conexión con la estación y sincroniza la cola de eventos pendientes.
    """
    while True:
        writer = None
        try:
            reader, writer = await asyncio.open_connection(HOST_ESTACION, PORT_ESTACION)
            print(f"✅ Conectado a la estación en {HOST_ESTACION}:{PORT_ESTACION}")

            # 1. Sincronizar todos los eventos pendientes
            while eventos_pendientes:
                evento = eventos_pendientes[0] # Peek
                data_a_enviar = (json.dumps(evento) + "\n").encode()
                writer.write(data_a_enviar)
                await writer.drain()
                eventos_pendientes.popleft() # Pop only after successful send
                print(f"🔄 Evento pendiente sincronizado. Restantes: {len(eventos_pendientes)}")
                await asyncio.sleep(0.1)

            print("✅ Cola de eventos vacía y sincronizada.")

            # 2. Mantener la conexión viva escuchando datos
            while not reader.at_eof():
                await reader.read(1024) # Espera pasiva de datos

        except (ConnectionRefusedError, OSError) as e:
            print(f"🔌 No se pudo conectar a la estación: {e}. Los nuevos eventos se encolarán.")
        except Exception as e:
            print(f"❌ Error inesperado en la conexión TCP: {e}. Los nuevos eventos se encolarán.")
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
        
        await asyncio.sleep(5) # Esperar 5 segundos antes de reintentar la conexión

# --- Simulación de carga de combustible ---
async def simular_carga():
    while True:
        if surtidor["estado"] == "Cargando combustible":
            await asyncio.sleep(1)
            surtidor["litros_despachados"] += 1
            surtidor["total_cobrado"] = surtidor["litros_despachados"] * surtidor["precio_litro"]
            print(f"💧 Cargando... {surtidor['litros_despachados']:.1f} L - ${surtidor['total_cobrado']:.0f}")
        else:
            # Evita un bucle ocupado cuando no está cargando
            await asyncio.sleep(1)

# --- Eventos de inicio de FastAPI ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(conectar_y_sincronizar())
    asyncio.create_task(simular_carga())

# --- Endpoints de la API ---
@app.get("/estado")
async def get_estado():
    """Obtiene el estado actual del surtidor."""
    return surtidor

@app.post("/control/iniciar-carga")
async def iniciar_carga():
    """Inicia la carga de combustible y encola el evento."""
    if surtidor["estado"] == "Parado":
        surtidor["estado"] = "Cargando combustible"
        surtidor["litros_despachados"] = 0.0
        surtidor["total_cobrado"] = 0.0
        await encolar_estado_actual()
        return {"mensaje": "Carga iniciada"}
    raise HTTPException(status_code=400, detail="El surtidor no está parado.")

@app.post("/control/detener-carga")
async def detener_carga():
    """Detiene la carga, finaliza la transacción y encola el evento."""
    if surtidor["estado"] == "Cargando combustible":
        surtidor["estado"] = "Parado"
        await encolar_estado_actual()
        return {"mensaje": f"Carga detenida. Total: ${surtidor['total_cobrado']:.0f}"}
    raise HTTPException(status_code=400, detail="El surtidor no está cargando combustible.")

@app.put("/configuracion")
async def update_config(nombre: str, precio_litro: int):
    """Actualiza la configuración del surtidor y encola el evento."""
    surtidor["nombre"] = nombre
    surtidor["precio_litro"] = precio_litro
    await encolar_estado_actual()
    return {"mensaje": "Configuración actualizada", "nuevo_estado": surtidor}
