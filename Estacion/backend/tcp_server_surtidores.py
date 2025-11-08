"""
Servidor TCP/UDP para manejar conexiones de surtidores
Puerto TCP: 6000 (conexión persistente, transacciones, comandos)
Puerto UDP: 6001 (estados en tiempo real, bajo overhead)
Protocolo: Socket TCP puro + UDP (NO WebSocket)
Formato: Mensajes JSON delimitados por \n (TCP) o JSON puro (UDP)
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Tuple
from database import obtener_database
from surtidores_service import (
    actualizar_conexion_surtidor,
    actualizar_estadisticas_surtidor,
    obtener_surtidor_por_id
)
from tcp_server import obtener_precios_actuales

# Diccionario de surtidores conectados: {id_surtidor: writer}
surtidores_conectados: Dict[int, asyncio.StreamWriter] = {}

# Set de writers para envío de mensajes broadcast
clientes_surtidores: Set[asyncio.StreamWriter] = set()

# Diccionario de direcciones UDP de surtidores: {id_surtidor: (ip, puerto)}
surtidores_udp: Dict[int, Tuple[str, int]] = {}


async def manejar_conexion_surtidor(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Maneja la conexión TCP de un surtidor individual
    Protocolo: Socket TCP puro con mensajes JSON delimitados por \n
    """
    addr = writer.get_extra_info('peername')
    id_surtidor = None
    
    try:
        print(f"🔌 Nueva conexión TCP desde {addr}")
        
        # Esperar mensaje de registro (timeout 10 segundos)
        registro_data = await asyncio.wait_for(reader.readline(), timeout=10.0)
        
        if not registro_data:
            print(f"⚠️ Conexión cerrada sin registro desde {addr}")
            return
        
        # Decodificar mensaje JSON
        registro = json.loads(registro_data.decode())
        
        if registro.get("tipo") != "registro":
            print(f"⚠️ Primer mensaje no es registro: {registro}")
            writer.close()
            await writer.wait_closed()
            return
        
        id_surtidor = registro.get("id_surtidor")
        
        if not id_surtidor:
            print(f"⚠️ Registro sin id_surtidor: {registro}")
            writer.close()
            await writer.wait_closed()
            return
        
        # Verificar que el surtidor existe en la BD
        surtidor = await obtener_surtidor_por_id(id_surtidor)
        
        if not surtidor:
            print(f"❌ Surtidor {id_surtidor} no registrado en la BD")
            # Enviar error
            error_msg = {
                "tipo": "error",
                "codigo": "SURTIDOR_NO_REGISTRADO",
                "mensaje": f"Surtidor {id_surtidor} no existe. Debe registrarse primero en la estación."
            }
            writer.write((json.dumps(error_msg) + "\n").encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        
        print(f"✅ Surtidor {id_surtidor} ({surtidor['nombre']}) conectado vía TCP")
        
        # Registrar conexión
        surtidores_conectados[id_surtidor] = writer
        clientes_surtidores.add(writer)
        await actualizar_conexion_surtidor(id_surtidor, "conectado")
        
        # Enviar confirmación con precios actuales
        precios = obtener_precios_actuales()
        confirmacion = {
            "tipo": "registro_confirmado",
            "id_surtidor": id_surtidor,
            "mensaje": "Surtidor registrado exitosamente",
            "precios": precios
        }
        writer.write((json.dumps(confirmacion) + "\n").encode())
        await writer.drain()
        print(f"📤 Confirmación enviada a surtidor {id_surtidor}")
        
        # Loop principal: recibir mensajes del surtidor
        last_heartbeat = datetime.now()
        
        while True:
            try:
                # Timeout de 90 segundos (esperamos heartbeat cada 30s)
                data = await asyncio.wait_for(reader.readline(), timeout=90.0)
                
                if not data:
                    print(f"⚠️ Conexión cerrada por surtidor {id_surtidor}")
                    break
                
                # Decodificar mensaje JSON
                mensaje = json.loads(data.decode())
                last_heartbeat = datetime.now()
                
                # Procesar mensaje según tipo
                await procesar_mensaje_surtidor(id_surtidor, mensaje)
                
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout: Surtidor {id_surtidor} sin heartbeat por 90s")
                break
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON inválido desde surtidor {id_surtidor}: {e}")
                # No cerrar conexión, solo ignorar mensaje malo
            except Exception as e:
                print(f"❌ Error procesando mensaje de surtidor {id_surtidor}: {e}")
                break
    
    except asyncio.TimeoutError:
        print(f"⏱️ Timeout esperando registro desde {addr}")
    except json.JSONDecodeError as e:
        print(f"⚠️ Error decodificando JSON desde {addr}: {e}")
    except Exception as e:
        print(f"❌ Error en conexión TCP desde {addr}: {e}")
    finally:
        # Limpiar conexión
        if id_surtidor:
            print(f"❌ Surtidor {id_surtidor} desconectado")
            surtidores_conectados.pop(id_surtidor, None)
            await actualizar_conexion_surtidor(id_surtidor, "desconectado")
        
        clientes_surtidores.discard(writer)
        writer.close()
        await writer.wait_closed()


async def procesar_mensaje_surtidor(id_surtidor: int, mensaje: dict):
    """
    Procesa diferentes tipos de mensajes recibidos de un surtidor vía TCP
    
    Args:
        id_surtidor: ID del surtidor que envió el mensaje
        mensaje: Diccionario con el mensaje JSON
    """
    tipo = mensaje.get("tipo")
    
    if tipo == "estado":
        # Actualización de estado en tiempo real
        estado_op = mensaje.get("estado_operacion", "desconocido")
        litros = mensaje.get("litros_actuales", 0)
        print(f"📊 Estado surtidor {id_surtidor}: {estado_op} - {litros}L")
        # Aquí puedes actualizar un cache en memoria o Redis si necesitas
        # estado en tiempo real para el frontend
        
    elif tipo == "transaccion_completada":
        # Guardar transacción en la BD
        print(f"💰 Transacción completada en surtidor {id_surtidor}")
        await guardar_transaccion(id_surtidor, mensaje)
        
    elif tipo == "heartbeat":
        # Mantener la conexión viva (no hacer nada, solo resetea el timeout)
        pass
    
    elif tipo == "registro_udp":
        # Registrar dirección UDP del surtidor
        ip = mensaje.get("ip")
        puerto = mensaje.get("puerto")
        if ip and puerto:
            surtidores_udp[id_surtidor] = (ip, puerto)
            print(f"📡 Surtidor {id_surtidor} registró UDP en {ip}:{puerto}")
        
    elif tipo == "error":
        codigo = mensaje.get("codigo", "ERROR_DESCONOCIDO")
        msg = mensaje.get("mensaje", "Error sin descripción")
        print(f"🚨 Error en surtidor {id_surtidor} [{codigo}]: {msg}")
        # Aquí puedes registrar en logs, enviar alertas, etc.
        
    else:
        print(f"⚠️ Tipo de mensaje desconocido desde surtidor {id_surtidor}: {tipo}")


async def guardar_transaccion(id_surtidor: int, datos: dict):
    """
    Guarda una transacción completada en la base de datos
    
    Args:
        id_surtidor: ID del surtidor
        datos: Datos de la transacción (JSON del mensaje)
    """
    try:
        db = obtener_database()
        
        # Obtener datos del surtidor
        surtidor = await obtener_surtidor_por_id(id_surtidor)
        
        # Preparar documento de transacción
        transaccion = {
            "surtidor_id": str(id_surtidor),
            "nombre_surtidor": surtidor["nombre"] if surtidor else f"Surtidor {id_surtidor}",
            "tipo_combustible": datos.get("tipo_combustible"),
            "litros": datos.get("litros"),
            "precio_por_litro": datos.get("precio_por_litro"),
            "monto_total": datos.get("monto_total"),
            "metodo_pago": datos.get("metodo_pago", "efectivo"),
            "fecha": datetime.fromisoformat(datos.get("fecha_fin")) if datos.get("fecha_fin") else datetime.now(),
            "estado": "completada"
        }
        
        # Insertar transacción
        resultado = await db.transacciones.insert_one(transaccion)
        
        # Actualizar estadísticas del surtidor
        await actualizar_estadisticas_surtidor(
            id_surtidor,
            datos.get("litros", 0),
            datos.get("monto_total", 0)
        )
        
        print(f"✅ Transacción guardada: {resultado.inserted_id} - {datos.get('litros')}L - ${datos.get('monto_total')}")
        
    except Exception as e:
        print(f"❌ Error guardando transacción: {e}")


async def propagar_precios_a_surtidores(nuevos_precios: dict):
    """
    Propaga actualización de precios a todos los surtidores conectados
    Usa socket TCP puro (NO WebSocket)
    
    Args:
        nuevos_precios: Diccionario con los nuevos precios
    """
    if not surtidores_conectados:
        print("⚠️ No hay surtidores conectados para propagar precios")
        return
    
    mensaje = {
        "tipo": "actualizacion_precios",
        "precios": nuevos_precios,
        "timestamp": datetime.now().isoformat()
    }
    
    # Convertir a JSON y agregar delimitador \n
    data = (json.dumps(mensaje) + "\n").encode()
    
    desconectados = []
    
    print(f"📡 Propagando precios a {len(surtidores_conectados)} surtidores...")
    
    for id_surtidor, writer in surtidores_conectados.items():
        try:
            writer.write(data)
            await writer.drain()
            print(f"✅ Precios enviados a surtidor {id_surtidor}")
        except Exception as e:
            print(f"❌ Error enviando precios a surtidor {id_surtidor}: {e}")
            desconectados.append(id_surtidor)
    
    # Limpiar conexiones muertas
    for id_surtidor in desconectados:
        surtidores_conectados.pop(id_surtidor, None)
        await actualizar_conexion_surtidor(id_surtidor, "desconectado")


async def enviar_comando_a_surtidor(id_surtidor: int, comando: str, razon: str = ""):
    """
    Envía un comando a un surtidor específico
    
    Args:
        id_surtidor: ID del surtidor
        comando: Comando a enviar (pausar, reanudar, detener_emergencia)
        razon: Razón del comando (opcional)
    
    Returns:
        True si se envió exitosamente, False si no está conectado
    """
    writer = surtidores_conectados.get(id_surtidor)
    
    if not writer:
        print(f"⚠️ Surtidor {id_surtidor} no está conectado")
        return False
    
    mensaje = {
        "tipo": "comando",
        "comando": comando,
        "razon": razon,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        data = (json.dumps(mensaje) + "\n").encode()
        writer.write(data)
        await writer.drain()
        print(f"📤 Comando '{comando}' enviado a surtidor {id_surtidor}")
        return True
    except Exception as e:
        print(f"❌ Error enviando comando a surtidor {id_surtidor}: {e}")
        return False


class UDPServerProtocol(asyncio.DatagramProtocol):
    """
    Protocolo UDP para recibir estados en tiempo real de surtidores
    Usado cuando el surtidor está ocupado despachando (baja latencia)
    """
    
    def __init__(self):
        self.transport = None
    
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        """
        Recibe datagramas UDP con estados de surtidores
        No se garantiza orden ni entrega, pero es muy rápido
        """
        try:
            mensaje = json.loads(data.decode())
            id_surtidor = mensaje.get("id_surtidor")
            tipo = mensaje.get("tipo")
            
            if tipo == "estado_rapido":
                # Estado durante despacho (no crítico si se pierde)
                estado_op = mensaje.get("estado_operacion", "desconocido")
                litros = mensaje.get("litros_actuales", 0)
                monto = mensaje.get("monto_actual", 0)
                print(f"⚡ UDP Estado surtidor {id_surtidor}: {estado_op} - {litros}L - ${monto}")
                # Aquí puedes actualizar cache/Redis para frontend en tiempo real
            
            elif tipo == "registro_udp":
                # El surtidor nos informa su puerto UDP
                if id_surtidor:
                    surtidores_udp[id_surtidor] = addr
                    print(f"📡 Surtidor {id_surtidor} registrado UDP desde {addr}")
                    
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON inválido en UDP: {e}")
        except Exception as e:
            print(f"❌ Error procesando UDP: {e}")


async def iniciar_servidor_udp_surtidores():
    """
    Inicia el servidor UDP para recibir estados rápidos de surtidores
    Puerto: 6001
    Protocolo: UDP con JSON (sin delimitadores)
    """
    loop = asyncio.get_running_loop()
    
    # Crear servidor UDP
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=("0.0.0.0", 6001)
    )
    
    print(f"🟢 Servidor UDP Surtidores escuchando en 0.0.0.0:6001")
    print(f"   Protocolo: UDP (estados rápidos en tiempo real)")


async def iniciar_servidor_tcp_surtidores():
    """
    Inicia el servidor TCP para escuchar conexiones de surtidores
    Puerto: 6000
    Protocolo: Socket TCP puro (NO WebSocket)
    """
    server = await asyncio.start_server(
        manejar_conexion_surtidor,
        "0.0.0.0",
        6000
    )
    
    addr = server.sockets[0].getsockname()
    print(f"🟢 Servidor TCP Surtidores escuchando en {addr[0]}:{addr[1]}")
    print(f"   Protocolo: Socket TCP puro (JSON + \\n)")
    
    async with server:
        await server.serve_forever()


async def iniciar_servidores_surtidores():
    """
    Inicia ambos servidores (TCP y UDP) en paralelo
    TCP: Conexión persistente, transacciones, comandos
    UDP: Estados rápidos en tiempo real (surtidor ocupado)
    """
    # Iniciar UDP en background
    asyncio.create_task(iniciar_servidor_udp_surtidores())
    
    # Iniciar TCP (bloquea aquí)
    await iniciar_servidor_tcp_surtidores()


def obtener_surtidores_activos() -> Dict[int, asyncio.StreamWriter]:
    """
    Retorna el diccionario de surtidores actualmente conectados vía TCP
    
    Returns:
        Diccionario con {id_surtidor: writer}
    """
    return surtidores_conectados.copy()


def obtener_cantidad_surtidores_conectados() -> int:
    """
    Retorna la cantidad de surtidores actualmente conectados
    
    Returns:
        Número de surtidores conectados
    """
    return len(surtidores_conectados)


def obtener_surtidores_udp_registrados() -> Dict[int, Tuple[str, int]]:
    """
    Retorna el diccionario de surtidores con UDP registrado
    
    Returns:
        Diccionario con {id_surtidor: (ip, puerto)}
    """
    return surtidores_udp.copy()
