"""
Configuración de conexión a MongoDB usando Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "bencineras_db")

# Cliente de MongoDB
client = AsyncIOMotorClient(MONGODB_URL)

# Base de datos
db = client[DATABASE_NAME]

# Colecciones
estaciones_collection = db["estaciones"]

# Función para verificar la conexión
async def verificar_conexion():
    """Verifica que la conexión a MongoDB esté funcionando"""
    try:
        await client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False

# Función para cerrar la conexión
async def cerrar_conexion():
    """Cierra la conexión a MongoDB"""
    client.close()
    print("🔒 Conexión a MongoDB cerrada")
