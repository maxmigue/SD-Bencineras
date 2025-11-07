import asyncio
import json
import socket
from datetime import datetime
from typing import Dict, Any

# Mantendrá el estado actual de los surtidores conectados
surtidores = {}
# Lista global de clientes conectados (writers)
clientes_conectados = set()
# Registro de estaciones conectadas con su información
estaciones_activas: Dict[str, Dict[str, Any]] = {}

async def manejar_surtidor(reader, writer):
    addr = writer.get_extra_info('peername')
    surtidor_id = f"{addr[0]}:{addr[1]}"
    print(f"🔌 Nueva conexión de surtidor {surtidor_id}")
    surtidores[surtidor_id] = {"estado": "Conectado"}
    clientes_conectados.add(writer)

    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            try:
                mensaje = json.loads(data.decode())
                surtidores[surtidor_id] = mensaje
                print(f"📡 Estado recibido de {surtidor_id}: {mensaje}")

                # 🔄 Reenviar a todos los clientes conectados (excepto al que lo envió)
                for cliente in list(clientes_conectados):
                    if cliente != writer:
                        try:
                            cliente.write(data)
                            await cliente.drain()
                        except Exception as e:
                            print(f"⚠️ Error enviando a cliente: {e}")
                            clientes_conectados.discard(cliente)

            except json.JSONDecodeError:
                print(f"⚠️ Mensaje inválido desde {surtidor_id}: {data.decode()}")

    except Exception as e:
        print(f"⚠️ Error en surtidor {surtidor_id}: {e}")

    finally:
        print(f"❌ Surtidor desconectado {surtidor_id}")
        surtidores.pop(surtidor_id, None)
        clientes_conectados.discard(writer)
        writer.close()
        await writer.wait_closed()

async def iniciar_tcp_servidor():
    """Inicia el servidor TCP que recibe los estados de los surtidores."""
    server = await asyncio.start_server(manejar_surtidor, "127.0.0.1", 5000)
    print("🟢 Servidor TCP escuchando en 127.0.0.1:5000")
    async with server:
        await server.serve_forever()


async def enviar_precios_a_estacion(ip: str, puerto: int, precios: Dict[str, int], nombre_estacion: str = None) -> bool:
    """
    Envía los precios actualizados a una estación específica vía TCP
    
    Args:
        ip: Dirección IP de la estación
        puerto: Puerto TCP de la estación
        precios: Diccionario con los precios actualizados
        nombre_estacion: Nombre de la estación (opcional)
        
    Returns:
        True si se envió exitosamente, False en caso de error
    """
    try:
        # Crear mensaje con el formato esperado
        mensaje = {
            "tipo": "actualizacion_precios",
            "timestamp": datetime.now().isoformat(),
            "precios": precios
        }
        
        # Agregar nombre si está disponible
        if nombre_estacion:
            mensaje["nombre_estacion"] = nombre_estacion
        
        print(f"📤 Enviando mensaje TCP: {mensaje}")
        
        # Conectar a la estación
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, puerto),
            timeout=5.0
        )
        
        # Enviar mensaje JSON
        mensaje_json = json.dumps(mensaje) + "\n"
        writer.write(mensaje_json.encode())
        await writer.drain()
        
        # Cerrar conexión
        writer.close()
        await writer.wait_closed()
        
        print(f"✅ Precios enviados exitosamente a {ip}:{puerto}")
        
        # Registrar la estación como activa
        estaciones_activas[f"{ip}:{puerto}"] = {
            "ip": ip,
            "puerto": puerto,
            "ultimo_envio": datetime.now().isoformat(),
            "estado": "conectada"
        }
        
        return True
        
    except asyncio.TimeoutError:
        print(f"⏱️ Timeout al conectar con {ip}:{puerto}")
        estaciones_activas[f"{ip}:{puerto}"] = {
            "ip": ip,
            "puerto": puerto,
            "ultimo_envio": None,
            "estado": "timeout"
        }
        return False
        
    except ConnectionRefusedError:
        print(f"❌ Conexión rechazada por {ip}:{puerto} - Estación no disponible")
        estaciones_activas[f"{ip}:{puerto}"] = {
            "ip": ip,
            "puerto": puerto,
            "ultimo_envio": None,
            "estado": "desconectada"
        }
        return False
        
    except Exception as e:
        print(f"❌ Error enviando precios a {ip}:{puerto}: {type(e).__name__} - {e}")
        estaciones_activas[f"{ip}:{puerto}"] = {
            "ip": ip,
            "puerto": puerto,
            "ultimo_envio": None,
            "estado": "error"
        }
        return False


def obtener_estaciones_activas() -> Dict[str, Dict[str, Any]]:
    """
    Retorna el registro de estaciones activas y su estado de conexión
    
    Returns:
        Diccionario con información de las estaciones
    """
    return estaciones_activas.copy()
