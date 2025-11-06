import socket
import json
import time
import random

HOST = "127.0.0.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("✅ Surtidor conectado al servidor")

surtidor = {
    "id": 1,
    "nombre": "Surtidor Norte",
    "estado": "Parado",
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
}

while True:
    # Alternar estado
    surtidor["estado"] = random.choice(["Cargando combustible", "Parado"])
    s.sendall((json.dumps(surtidor) + "\n").encode())
    print("📤 Enviado:", surtidor)
    time.sleep(5)
