import socket
import json
from datetime import datetime

# Configuración
HOST = "localhost"  # o "host.docker.internal" si pruebas desde contenedor
PORT = 5001  # Puerto mapeado del host

def test_enviar_precios():
    """Prueba enviar actualización de precios a la Estación"""
    try:
        # Crear socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        print(f"🔌 Intentando conectar a {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        print(f"✅ Conectado a {HOST}:{PORT}")
        
        # Crear mensaje de actualización de precios
        mensaje = {
            "tipo": "actualizacion_precios",
            "timestamp": datetime.now().isoformat(),
            "precios": {
                "precio_93": 9999,  # Precio de prueba muy alto para notar el cambio
                "precio_95": 9999,
                "precio_97": 9999,
                "precio_diesel": 9999
            }
        }
        
        # Enviar mensaje (debe terminar con \n)
        mensaje_json = json.dumps(mensaje) + "\n"
        sock.send(mensaje_json.encode())
        print(f"📤 Mensaje enviado: {mensaje}")
        
        print("✅ Prueba completada. Verifica el frontend de la Estación.")
        
        sock.close()
        
    except socket.timeout:
        print(f"⏱️ Timeout: No se pudo conectar a {HOST}:{PORT}")
        print("   Verifica que el contenedor de Estación esté corriendo")
        print("   Comando: docker ps | grep estacion")
        
    except ConnectionRefusedError:
        print(f"❌ Conexión rechazada en {HOST}:{PORT}")
        print("   Verifica que el puerto esté mapeado correctamente")
        print("   Comando: docker port <container_id>")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Test de conexión TCP a Estación")
    print("=" * 50)
    test_enviar_precios()
