import asyncio
import json
import os

# Mantendrá el estado actual de los surtidores conectados
surtidores = {}
# Lista global de clientes conectados (writers)
clientes_conectados = set()
# Precios actuales de la estación (actualizados por la Empresa)
precios_actuales = {
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
}
# Nombre de la estación (puede ser actualizado por la Empresa)
nombre_estacion = os.getenv("ESTACION_NOMBRE", "Estación Local")

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
                
                # 🔍 Detectar si es un mensaje de actualización de precios desde la Empresa
                if mensaje.get("tipo") == "actualizacion_precios":
                    print(f"💰 Actualización de precios recibida desde Empresa")
                    nuevos_precios = mensaje.get("precios", {})
                    
                    # Actualizar precios globales de la estación
                    precios_actuales.update(nuevos_precios)
                    print(f"✅ Precios actualizados: {precios_actuales}")
                    
                    # Actualizar nombre si viene en el mensaje
                    global nombre_estacion
                    if mensaje.get("nombre_estacion"):
                        nombre_estacion = mensaje.get("nombre_estacion")
                        print(f"✅ Nombre actualizado: {nombre_estacion}")
                    
                    # 📡 Propagar los nuevos precios a todos los clientes (frontend vía WebSocket bridge)
                    mensaje_propagacion = {
                        "tipo": "actualizacion_precios",
                        "timestamp": mensaje.get("timestamp"),
                        "precios": precios_actuales
                    }
                    
                    # Incluir nombre si fue actualizado
                    if mensaje.get("nombre_estacion"):
                        mensaje_propagacion["nombre_estacion"] = nombre_estacion
                    
                    data_propagacion = (json.dumps(mensaje_propagacion) + "\n").encode()
                    
                    for cliente in list(clientes_conectados):
                        try:
                            cliente.write(data_propagacion)
                            await cliente.drain()
                        except Exception as e:
                            print(f"⚠️ Error propagando precios a cliente: {e}")
                            clientes_conectados.discard(cliente)
                    
                    continue  # No procesar como mensaje de surtidor
                
                # Mensaje normal de surtidor
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
    server = await asyncio.start_server(manejar_surtidor, "0.0.0.0", 5000)
    print("🟢 Servidor TCP escuchando en 0.0.0.0:5000")
    async with server:
        await server.serve_forever()


def obtener_precios_actuales():
    """
    Retorna los precios actuales de la estación
    
    Returns:
        Diccionario con los precios actuales
    """
    return precios_actuales.copy()


def obtener_nombre_estacion():
    """
    Retorna el nombre actual de la estación
    
    Returns:
        Nombre de la estación
    """
    return nombre_estacion


def actualizar_precios_locales(nuevos_precios: dict):
    """
    Actualiza manualmente los precios locales
    Útil para testing o inicialización
    
    Args:
        nuevos_precios: Diccionario con los nuevos precios
    """
    precios_actuales.update(nuevos_precios)
    print(f"✅ Precios actualizados manualmente: {precios_actuales}")
