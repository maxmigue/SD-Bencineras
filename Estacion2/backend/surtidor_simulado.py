import socket
import json
import time
import random
import sys
import select

HOST = "127.0.0.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.setblocking(False)  # Socket no bloqueante para poder recibir mensajes
print("✅ Surtidor conectado al servidor")

# Precios iniciales (se actualizarán dinámicamente)
precios = {
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
}

surtidor = {
    "id": 1,
    "nombre": "Surtidor Norte",
    "estado": "Parado"
}

# Función para verificar si hay mensajes entrantes
def verificar_mensajes():
    """Verifica si hay mensajes del servidor y actualiza precios"""
    try:
        # Verificar si hay datos disponibles para leer
        ready = select.select([s], [], [], 0)
        if ready[0]:
            data = s.recv(4096)
            if data:
                try:
                    mensaje = json.loads(data.decode())
                    if mensaje.get("tipo") == "actualizacion_precios":
                        nuevos_precios = mensaje.get("precios", {})
                        precios.update(nuevos_precios)
                        print(f"💰 Precios actualizados desde servidor: {precios}")
                except json.JSONDecodeError:
                    pass
    except:
        pass

while True:
    # Verificar si hay actualizaciones de precios
    verificar_mensajes()
    
    # Alternar estado
    surtidor["estado"] = random.choice(["Cargando combustible", "Parado"])
    
    # Agregar precios actuales al mensaje
    surtidor.update(precios)
    
    # Enviar estado al servidor
    try:
        s.sendall((json.dumps(surtidor) + "\n").encode())
        print("📤 Enviado:", surtidor)
    except Exception as e:
        print(f"❌ Error enviando datos: {e}")
        break
    
    time.sleep(5)
