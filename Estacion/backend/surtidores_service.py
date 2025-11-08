"""
Servicios de gestión de surtidores
Implementa operaciones CRUD y lógica de negocio para surtidores
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import SurtidorCreate, SurtidorUpdate, SurtidorDB
from database import obtener_database
from bson import ObjectId


async def crear_surtidor(surtidor: SurtidorCreate, id_surtidor_manual: Optional[int] = None) -> Dict[str, Any]:
    """
    Crea un nuevo surtidor en la base de datos
    
    Args:
        surtidor: Datos del surtidor a crear
        id_surtidor_manual: ID específico para el surtidor (usado en auto-registro)
        
    Returns:
        Diccionario con los datos del surtidor creado
    """
    db = obtener_database()
    
    # Usar ID manual si se proporciona, sino auto-incrementar
    if id_surtidor_manual is not None:
        nuevo_id = id_surtidor_manual
        # Verificar que no exista
        existente = await db.surtidores.find_one({"id_surtidor": nuevo_id})
        if existente:
            raise ValueError(f"Ya existe un surtidor con ID {nuevo_id}")
    else:
        # Generar ID único autoincrementado
        ultimo_surtidor = await db.surtidores.find_one(sort=[("id_surtidor", -1)])
        nuevo_id = 1 if ultimo_surtidor is None else ultimo_surtidor["id_surtidor"] + 1
    
    # Preparar documento
    surtidor_dict = {
        "id_surtidor": nuevo_id,
        "nombre": surtidor.nombre,
        "estado": "disponible",
        "estado_conexion": "desconectado",
        "combustibles_soportados": surtidor.combustibles_soportados,
        "combustible_actual": surtidor.combustible_actual,
        "capacidad_maxima": surtidor.capacidad_maxima,
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now(),
        "ultima_conexion": None,
        "total_transacciones": 0,
        "litros_totales": 0.0,
        "ingresos_totales": 0
    }
    
    # Insertar en la base de datos
    resultado = await db.surtidores.insert_one(surtidor_dict)
    
    # Obtener el documento insertado
    surtidor_creado = await db.surtidores.find_one({"_id": resultado.inserted_id})
    
    if surtidor_creado:
        surtidor_creado["_id"] = str(surtidor_creado["_id"])
    
    return surtidor_creado


async def obtener_surtidores() -> List[Dict[str, Any]]:
    """
    Obtiene todos los surtidores registrados
    
    Returns:
        Lista de diccionarios con los datos de todos los surtidores
    """
    db = obtener_database()
    surtidores = []
    cursor = db.surtidores.find().sort("id_surtidor", 1)
    
    async for surtidor in cursor:
        surtidor["_id"] = str(surtidor["_id"])
        surtidores.append(surtidor)
    
    return surtidores


async def obtener_surtidor_por_id(id_surtidor: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un surtidor específico por su ID
    
    Args:
        id_surtidor: ID del surtidor
        
    Returns:
        Diccionario con los datos del surtidor o None si no existe
    """
    db = obtener_database()
    surtidor = await db.surtidores.find_one({"id_surtidor": id_surtidor})
    
    if surtidor:
        surtidor["_id"] = str(surtidor["_id"])
    
    return surtidor


async def actualizar_surtidor(
    id_surtidor: int,
    datos: SurtidorUpdate
) -> Optional[Dict[str, Any]]:
    """
    Actualiza la configuración de un surtidor
    
    Args:
        id_surtidor: ID del surtidor
        datos: Datos a actualizar
        
    Returns:
        Diccionario con los datos actualizados o None si no existe
    """
    db = obtener_database()
    
    # Preparar solo los campos que no son None
    datos_actualizacion = {}
    if datos.nombre is not None:
        datos_actualizacion["nombre"] = datos.nombre
    if datos.combustible_actual is not None:
        datos_actualizacion["combustible_actual"] = datos.combustible_actual
    if datos.capacidad_maxima is not None:
        datos_actualizacion["capacidad_maxima"] = datos.capacidad_maxima
    if datos.estado is not None:
        datos_actualizacion["estado"] = datos.estado
    
    datos_actualizacion["fecha_actualizacion"] = datetime.now()
    
    if len(datos_actualizacion) == 1:  # Solo fecha_actualizacion
        return await obtener_surtidor_por_id(id_surtidor)
    
    # Actualizar en la base de datos
    resultado = await db.surtidores.update_one(
        {"id_surtidor": id_surtidor},
        {"$set": datos_actualizacion}
    )
    
    if resultado.matched_count == 0:
        return None
    
    return await obtener_surtidor_por_id(id_surtidor)


async def eliminar_surtidor(id_surtidor: int) -> bool:
    """
    Elimina un surtidor de la base de datos
    
    Args:
        id_surtidor: ID del surtidor a eliminar
        
    Returns:
        True si se eliminó exitosamente, False si no existe
    """
    db = obtener_database()
    resultado = await db.surtidores.delete_one({"id_surtidor": id_surtidor})
    return resultado.deleted_count > 0


async def actualizar_estadisticas_surtidor(
    id_surtidor: int,
    litros: float,
    monto: int
):
    """
    Actualiza las estadísticas de un surtidor después de una transacción
    
    Args:
        id_surtidor: ID del surtidor
        litros: Litros despachados en la transacción
        monto: Monto total de la transacción
    """
    db = obtener_database()
    
    await db.surtidores.update_one(
        {"id_surtidor": id_surtidor},
        {
            "$inc": {
                "total_transacciones": 1,
                "litros_totales": litros,
                "ingresos_totales": monto
            },
            "$set": {
                "fecha_actualizacion": datetime.now()
            }
        }
    )


async def actualizar_conexion_surtidor(
    id_surtidor: int,
    estado_conexion: str
):
    """
    Actualiza el estado de conexión de un surtidor
    
    Args:
        id_surtidor: ID del surtidor
        estado_conexion: "conectado" o "desconectado"
    """
    db = obtener_database()
    
    datos = {
        "estado_conexion": estado_conexion,
        "fecha_actualizacion": datetime.now()
    }
    
    if estado_conexion == "conectado":
        datos["ultima_conexion"] = datetime.now()
    
    await db.surtidores.update_one(
        {"id_surtidor": id_surtidor},
        {"$set": datos}
    )


async def verificar_nombre_existente(nombre: str, excluir_id: Optional[int] = None) -> bool:
    """
    Verifica si ya existe un surtidor con el nombre especificado
    
    Args:
        nombre: Nombre a verificar
        excluir_id: ID a excluir de la búsqueda (útil al actualizar)
        
    Returns:
        True si el nombre ya existe, False si está disponible
    """
    db = obtener_database()
    query = {"nombre": nombre}
    if excluir_id is not None:
        query["id_surtidor"] = {"$ne": excluir_id}
    
    surtidor = await db.surtidores.find_one(query)
    return surtidor is not None


async def obtener_surtidores_conectados() -> List[Dict[str, Any]]:
    """
    Obtiene todos los surtidores actualmente conectados
    
    Returns:
        Lista de surtidores conectados
    """
    db = obtener_database()
    surtidores = []
    cursor = db.surtidores.find({"estado_conexion": "conectado"}).sort("id_surtidor", 1)
    
    async for surtidor in cursor:
        surtidor["_id"] = str(surtidor["_id"])
        surtidores.append(surtidor)
    
    return surtidores


async def obtener_estadisticas_surtidores() -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de todos los surtidores
    
    Returns:
        Diccionario con estadísticas agregadas
    """
    db = obtener_database()
    
    total = await db.surtidores.count_documents({})
    conectados = await db.surtidores.count_documents({"estado_conexion": "conectado"})
    disponibles = await db.surtidores.count_documents({"estado": "disponible"})
    
    # Agregación de estadísticas
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_transacciones": {"$sum": "$total_transacciones"},
                "total_litros": {"$sum": "$litros_totales"},
                "total_ingresos": {"$sum": "$ingresos_totales"}
            }
        }
    ]
    
    resultado = await db.surtidores.aggregate(pipeline).to_list(1)
    stats = resultado[0] if resultado else {
        "total_transacciones": 0,
        "total_litros": 0.0,
        "total_ingresos": 0
    }
    
    return {
        "total_surtidores": total,
        "conectados": conectados,
        "disponibles": disponibles,
        "total_transacciones": stats.get("total_transacciones", 0),
        "total_litros": stats.get("total_litros", 0.0),
        "total_ingresos": stats.get("total_ingresos", 0)
    }
