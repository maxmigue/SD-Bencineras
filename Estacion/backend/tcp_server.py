import asyncio
import json

# Mantendrá el estado actual de los surtidores conectados
surtidores = {}
# Lista global de clientes conectados (writers)
clientes_conectados = set()

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
