from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

# Variables de entorno
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27018")
DATABASE_NAME = os.getenv("DATABASE_NAME", "estacion_db")

# Cliente MongoDB global
mongodb_client: Optional[AsyncIOMotorClient] = None
database = None


async def conectar_db():
    """
    Conecta a MongoDB y crea índices necesarios
    """
    global mongodb_client, database
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        database = mongodb_client[DATABASE_NAME]
        
        # Verificar conexión
        await mongodb_client.admin.command('ping')
        print(f"✅ Conectado a MongoDB: {DATABASE_NAME}")
        
        # Crear índices para optimizar consultas
        await database.transacciones.create_index("fecha")
        await database.transacciones.create_index("surtidor_id")
        await database.transacciones.create_index("tipo_combustible")
        print("✅ Índices creados correctamente")
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        raise


async def desconectar_db():
    """
    Cierra la conexión a MongoDB
    """
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ Desconectado de MongoDB")


def obtener_database():
    """
    Obtiene la instancia de la base de datos
    
    Returns:
        Database instance
    """
    return database
