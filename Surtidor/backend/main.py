from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import socket
from datetime import datetime

# --- Configuración ---
ESTACION_HOST = os.getenv("ESTACION_HOST", "estacion-backend")
ESTACION_TCP_PORT = int(os.getenv("ESTACION_TCP_PORT", "6000"))
ESTACION_UDP_PORT = int(os.getenv("ESTACION_UDP_PORT", "6001"))
ID_SURTIDOR = int(os.getenv("ID_SURTIDOR", "1"))
NOMBRE_SURTIDOR = os.getenv("NOMBRE_SURTIDOR", f"Surtidor {ID_SURTIDOR}")

# --- Estado del Surtidor ---
surtidor = {
    "id_surtidor": ID_SURTIDOR,
    "nombre": NOMBRE_SURTIDOR,
    "estado_operacion": "disponible",  # disponible, despachando, pausado
    "tipo_combustible": "95",
    "litros_actuales": 0.0,
    "monto_actual": 0,
    "precio_litro": 1350,
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "fecha_inicio": None
}

# Precios actuales (actualizados por la estación)
precios = {
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
}

# Conexiones globales
writer_tcp_estacion = None  # TCP para transacciones y comandos
sock_udp = None  # UDP para estados rápidos

# --- FastAPI ---
app = FastAPI(
    title="API del Surtidor",
    description="Backend individual de un surtidor con TCP/UDP",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# CLIENTE TCP - CONEXIÓN PERSISTENTE
# ============================================

async def conectar_tcp_estacion():
    """Cliente TCP con reconexión automática"""
    global writer_tcp_estacion
    
    while True:
        try:
            reader, writer = await asyncio.open_connection(ESTACION_HOST, ESTACION_TCP_PORT)
            writer_tcp_estacion = writer
            print(f"✅ TCP conectado a estación en {ESTACION_HOST}:{ESTACION_TCP_PORT}")
            
            # Enviar mensaje de registro
            await enviar_registro_tcp()
            
            # Loop de recepción de mensajes
            while True:
                data = await reader.readline()
                
                if not data:
                    print("⚠️ Conexión TCP cerrada por la estación")
                    break
                
                try:
                    mensaje = json.loads(data.decode())
                    await procesar_mensaje_estacion(mensaje)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON inválido: {e}")
                    
        except ConnectionRefusedError:
            print(f"🔌 No se pudo conectar a estación TCP. Reintentando en 5s...")
            writer_tcp_estacion = None
        except Exception as e:
            print(f"❌ Error en conexión TCP: {e}")
            writer_tcp_estacion = None
        
        await asyncio.sleep(5)


async def enviar_registro_tcp():
    """Envía mensaje de registro inicial por TCP"""
    if writer_tcp_estacion:
        try:
            registro = {
                "tipo": "registro",
                "id_surtidor": ID_SURTIDOR,
                "nombre": NOMBRE_SURTIDOR,
                "combustibles_soportados": surtidor["combustibles_soportados"],
                "version": "2.0"
            }
            data = (json.dumps(registro) + "\n").encode()
            writer_tcp_estacion.write(data)
            await writer_tcp_estacion.drain()
            print(f"📤 Registro TCP enviado: ID={ID_SURTIDOR}")
        except Exception as e:
            print(f"❌ Error enviando registro TCP: {e}")


async def procesar_mensaje_estacion(mensaje: dict):
    """Procesa mensajes recibidos de la estación vía TCP"""
    tipo = mensaje.get("tipo")
    
    if tipo == "registro_confirmado":
        print(f"✅ Registro confirmado: {mensaje.get('mensaje')}")
        nuevos_precios = mensaje.get("precios", {})
        precios.update(nuevos_precios)
        actualizar_precio_actual()
        
    elif tipo == "actualizacion_precios":
        print(f"💰 Actualización de precios recibida")
        nuevos_precios = mensaje.get("precios", {})
        precios.update(nuevos_precios)
        actualizar_precio_actual()
        
    elif tipo == "comando":
        comando = mensaje.get("comando")
        print(f"🎮 Comando recibido: {comando}")
        await ejecutar_comando(comando, mensaje.get("razon", ""))
        
    elif tipo == "error":
        print(f"🚨 Error desde estación: {mensaje.get('mensaje')}")


async def ejecutar_comando(comando: str, razon: str):
    """Ejecuta comandos recibidos desde la estación"""
    if comando == "pausar" and surtidor["estado_operacion"] == "despachando":
        surtidor["estado_operacion"] = "pausado"
        print(f"⏸️ Surtidor pausado: {razon}")
        await enviar_estado_tcp()
    elif comando == "reanudar" and surtidor["estado_operacion"] == "pausado":
        surtidor["estado_operacion"] = "despachando"
        print(f"▶️ Surtidor reanudado")
        await enviar_estado_tcp()
    elif comando == "detener_emergencia":
        surtidor["estado_operacion"] = "disponible"
        surtidor["litros_actuales"] = 0.0
        surtidor["monto_actual"] = 0
        print(f"🚨 Detención de emergencia: {razon}")
        await enviar_estado_tcp()


def actualizar_precio_actual():
    """Actualiza el precio actual según el combustible configurado"""
    tipo = surtidor["tipo_combustible"]
    if tipo == "93":
        surtidor["precio_litro"] = precios["precio_93"]
    elif tipo == "95":
        surtidor["precio_litro"] = precios["precio_95"]
    elif tipo == "97":
        surtidor["precio_litro"] = precios["precio_97"]
    elif tipo == "diesel":
        surtidor["precio_litro"] = precios["precio_diesel"]
    print(f"💰 Precio actualizado: ${surtidor['precio_litro']}/L")


async def enviar_estado_tcp():
    """Envía el estado actual por TCP"""
    if writer_tcp_estacion:
        try:
            estado = {
                "tipo": "estado",
                "id_surtidor": ID_SURTIDOR,
                "estado_operacion": surtidor["estado_operacion"],
                "litros_actuales": surtidor["litros_actuales"],
                "monto_actual": surtidor["monto_actual"],
                "tipo_combustible": surtidor["tipo_combustible"],
                "timestamp": datetime.now().isoformat()
            }
            data = (json.dumps(estado) + "\n").encode()
            writer_tcp_estacion.write(data)
            await writer_tcp_estacion.drain()
        except Exception as e:
            print(f"❌ Error enviando estado TCP: {e}")


async def enviar_transaccion_completada(transaccion_data: dict):
    """Envía una transacción completada a la estación por TCP"""
    if writer_tcp_estacion:
        try:
            mensaje = {
                "tipo": "transaccion_completada",
                "id_surtidor": ID_SURTIDOR,
                "tipo_combustible": transaccion_data["tipo_combustible"],
                "litros": transaccion_data["litros"],
                "precio_por_litro": transaccion_data["precio_por_litro"],
                "monto_total": transaccion_data["monto_total"],
                "metodo_pago": transaccion_data["metodo_pago"],
                "fecha_inicio": transaccion_data["fecha_inicio"],
                "fecha_fin": datetime.now().isoformat()
            }
            data = (json.dumps(mensaje) + "\n").encode()
            writer_tcp_estacion.write(data)
            await writer_tcp_estacion.drain()
            print(f"✅ Transacción enviada: {transaccion_data['litros']}L")
        except Exception as e:
            print(f"❌ Error enviando transacción TCP: {e}")


async def heartbeat_tcp_task():
    """Envía heartbeat cada 30 segundos por TCP"""
    while True:
        await asyncio.sleep(30)
        if writer_tcp_estacion:
            try:
                heartbeat = {
                    "tipo": "heartbeat",
                    "id_surtidor": ID_SURTIDOR,
                    "timestamp": datetime.now().isoformat()
                }
                data = (json.dumps(heartbeat) + "\n").encode()
                writer_tcp_estacion.write(data)
                await writer_tcp_estacion.drain()
            except Exception as e:
                print(f"⚠️ Error enviando heartbeat: {e}")


# ============================================
# CLIENTE UDP - ESTADOS RÁPIDOS
# ============================================

def inicializar_udp():
    """Inicializa socket UDP para enviar estados rápidos"""
    global sock_udp
    try:
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"✅ Socket UDP inicializado")
    except Exception as e:
        print(f"❌ Error inicializando UDP: {e}")


def enviar_estado_udp():
    """Envía estado rápido por UDP (durante despacho)"""
    if sock_udp:
        try:
            mensaje = {
                "tipo": "estado_rapido",
                "id_surtidor": ID_SURTIDOR,
                "estado_operacion": surtidor["estado_operacion"],
                "litros_actuales": surtidor["litros_actuales"],
                "monto_actual": surtidor["monto_actual"],
                "tipo_combustible": surtidor["tipo_combustible"],
                "timestamp": datetime.now().isoformat()
            }
            data = json.dumps(mensaje).encode()
            sock_udp.sendto(data, (ESTACION_HOST, ESTACION_UDP_PORT))
        except Exception as e:
            print(f"⚠️ Error enviando UDP: {e}")


# ============================================
# SIMULACIÓN DE CARGA
# ============================================

async def simular_carga():
    """Simula el despacho de combustible"""
    contador = 0
    while True:
        if surtidor["estado_operacion"] == "despachando":
            await asyncio.sleep(1)
            surtidor["litros_actuales"] += 1.0
            surtidor["monto_actual"] = int(surtidor["litros_actuales"] * surtidor["precio_litro"])
            
            # UDP cada segundo (rápido)
            enviar_estado_udp()
            contador += 1
            
            # TCP cada 5 segundos (backup)
            if contador % 5 == 0:
                await enviar_estado_tcp()
        else:
            contador = 0
        
        await asyncio.sleep(1)


# ============================================
# EVENTOS DE FASTAPI
# ============================================

@app.on_event("startup")
async def startup_event():
    print(f"🚀 Iniciando Surtidor ID={ID_SURTIDOR} ({NOMBRE_SURTIDOR})")
    
    # Inicializar UDP
    inicializar_udp()
    
    # Iniciar conexión TCP
    asyncio.create_task(conectar_tcp_estacion())
    
    # Iniciar simulación de carga
    asyncio.create_task(simular_carga())
    
    # Iniciar heartbeat
    asyncio.create_task(heartbeat_tcp_task())


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def home():
    return {
        "surtidor_id": ID_SURTIDOR,
        "nombre": NOMBRE_SURTIDOR,
        "status": "ok",
        "version": "2.0"
    }


@app.get("/estado")
async def get_estado():
    """Obtiene el estado actual del surtidor"""
    return {
        **surtidor,
        "precios_disponibles": precios,
        "conectado_tcp": writer_tcp_estacion is not None,
        "udp_habilitado": sock_udp is not None
    }


@app.post("/control/iniciar-carga")
async def iniciar_carga():
    """Inicia la carga de combustible"""
    if surtidor["estado_operacion"] == "disponible":
        surtidor["estado_operacion"] = "despachando"
        surtidor["litros_actuales"] = 0.0
        surtidor["monto_actual"] = 0
        surtidor["fecha_inicio"] = datetime.now().isoformat()
        await enviar_estado_tcp()
        return {"mensaje": "Carga iniciada", "estado": surtidor}
    raise HTTPException(status_code=400, detail="El surtidor no está disponible.")


@app.post("/control/detener-carga")
async def detener_carga(metodo_pago: str = "efectivo"):
    """Detiene la carga y registra la transacción"""
    if surtidor["estado_operacion"] == "despachando":
        # Preparar datos de transacción
        transaccion = {
            "tipo_combustible": surtidor["tipo_combustible"],
            "litros": surtidor["litros_actuales"],
            "precio_por_litro": surtidor["precio_litro"],
            "monto_total": surtidor["monto_actual"],
            "metodo_pago": metodo_pago,
            "fecha_inicio": surtidor.get("fecha_inicio", datetime.now().isoformat())
        }
        
        # Cambiar estado
        surtidor["estado_operacion"] = "disponible"
        
        # Enviar transacción a la estación por TCP
        await enviar_transaccion_completada(transaccion)
        
        # Resetear valores
        resultado = {
            "mensaje": "Carga completada y transacción registrada",
            "litros": surtidor["litros_actuales"],
            "total": surtidor["monto_actual"],
            "metodo_pago": metodo_pago
        }
        
        surtidor["litros_actuales"] = 0.0
        surtidor["monto_actual"] = 0
        
        await enviar_estado_tcp()
        
        return resultado
    
    raise HTTPException(status_code=400, detail="El surtidor no está despachando.")


@app.put("/configuracion")
async def actualizar_configuracion(
    tipo_combustible: str = None,
    nombre: str = None
):
    """Actualiza la configuración del surtidor"""
    if surtidor["estado_operacion"] == "despachando":
        raise HTTPException(
            status_code=400,
            detail="No se puede cambiar configuración durante despacho"
        )
    
    cambios = False
    
    if tipo_combustible and tipo_combustible in surtidor["combustibles_soportados"]:
        surtidor["tipo_combustible"] = tipo_combustible
        actualizar_precio_actual()
        cambios = True
    
    if nombre:
        surtidor["nombre"] = nombre
        cambios = True
    
    if cambios:
        await enviar_estado_tcp()
        return {"mensaje": "Configuración actualizada", "estado": surtidor}
    
    raise HTTPException(status_code=400, detail="No se especificaron cambios válidos")


@app.get("/precios")
def obtener_precios():
    """Obtiene los precios actuales de todos los combustibles"""
    return precios


@app.get("/health")
def health_check():
    """Health check para Docker/Kubernetes"""
    return {
        "status": "healthy",
        "tcp_connected": writer_tcp_estacion is not None,
        "udp_enabled": sock_udp is not None,
        "estado_operacion": surtidor["estado_operacion"]
    }
