"""
Servicios de base de datos para la gestión de estaciones
Implementa las operaciones CRUD para las estaciones de servicio
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import (
    EstacionCreate, 
    EstacionUpdate, 
    PreciosUpdate,
    HistoricoPreciosModel
)
from database import estaciones_collection


async def crear_estacion(estacion: EstacionCreate) -> Dict[str, Any]:
    """
    Crea una nueva estación en la base de datos
    
    Args:
        estacion: Datos de la estación a crear
        
    Returns:
        Diccionario con los datos de la estación creada
    """
    # Generar ID único (obtener el máximo ID actual + 1)
    ultima_estacion = await estaciones_collection.find_one(
        sort=[("id_estacion", -1)]
    )
    nuevo_id = 1 if ultima_estacion is None else ultima_estacion["id_estacion"] + 1
    
    # Preparar documento para insertar
    estacion_dict = {
        "id_estacion": nuevo_id,
        "nombre": estacion.nombre,
        "ip": estacion.ip,
        "puerto": estacion.puerto,
        "estado": "Activa",
        "precios_actuales": estacion.precios_actuales.model_dump(),
        "historico_precios": [
            {
                "timestamp": datetime.now(),
                "precios": estacion.precios_actuales.model_dump()
            }
        ],
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now()
    }
    
    # Insertar en la base de datos
    resultado = await estaciones_collection.insert_one(estacion_dict)
    
    # Obtener el documento insertado
    estacion_creada = await estaciones_collection.find_one(
        {"_id": resultado.inserted_id}
    )
    
    # Convertir ObjectId a string para serialización JSON
    if estacion_creada:
        estacion_creada["_id"] = str(estacion_creada["_id"])
    
    return estacion_creada


async def obtener_estaciones() -> List[Dict[str, Any]]:
    """
    Obtiene todas las estaciones de la base de datos
    
    Returns:
        Lista de diccionarios con los datos de todas las estaciones
    """
    estaciones = []
    cursor = estaciones_collection.find()
    
    async for estacion in cursor:
        estacion["_id"] = str(estacion["_id"])
        estaciones.append(estacion)
    
    return estaciones


async def obtener_estacion_por_id(id_estacion: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una estación específica por su ID
    
    Args:
        id_estacion: ID de la estación a buscar
        
    Returns:
        Diccionario con los datos de la estación o None si no existe
    """
    estacion = await estaciones_collection.find_one({"id_estacion": id_estacion})
    
    if estacion:
        estacion["_id"] = str(estacion["_id"])
    
    return estacion


async def actualizar_estacion(
    id_estacion: int, 
    datos: EstacionUpdate
) -> Optional[Dict[str, Any]]:
    """
    Actualiza los datos generales de una estación (nombre, IP, puerto, estado)
    No actualiza precios - usar actualizar_precios() para eso
    
    Args:
        id_estacion: ID de la estación a actualizar
        datos: Datos a actualizar (solo los campos no None)
        
    Returns:
        Diccionario con los datos actualizados o None si no existe la estación
    """
    # Preparar solo los campos que no son None
    datos_actualizacion = {}
    if datos.nombre is not None:
        datos_actualizacion["nombre"] = datos.nombre
    if datos.ip is not None:
        datos_actualizacion["ip"] = datos.ip
    if datos.puerto is not None:
        datos_actualizacion["puerto"] = datos.puerto
    if datos.estado is not None:
        datos_actualizacion["estado"] = datos.estado
    
    # Siempre actualizar fecha de modificación
    datos_actualizacion["fecha_actualizacion"] = datetime.now()
    
    if not datos_actualizacion:
        # No hay nada que actualizar (solo fecha)
        return await obtener_estacion_por_id(id_estacion)
    
    # Actualizar en la base de datos
    resultado = await estaciones_collection.update_one(
        {"id_estacion": id_estacion},
        {"$set": datos_actualizacion}
    )
    
    if resultado.matched_count == 0:
        return None
    
    # Obtener y retornar la estación actualizada
    return await obtener_estacion_por_id(id_estacion)


async def actualizar_precios(
    id_estacion: int,
    precios_update: PreciosUpdate
) -> Optional[Dict[str, Any]]:
    """
    Actualiza los precios de una estación y agrega una entrada al historial
    
    Args:
        id_estacion: ID de la estación
        precios_update: Nuevos precios a establecer
        
    Returns:
        Diccionario con los datos actualizados o None si no existe la estación
    """
    # Verificar que la estación existe
    estacion = await obtener_estacion_por_id(id_estacion)
    if not estacion:
        return None
    
    # Preparar entrada para el historial
    entrada_historial = {
        "timestamp": datetime.now(),
        "precios": precios_update.precios.model_dump()
    }
    
    # Actualizar precios actuales y agregar al historial
    resultado = await estaciones_collection.update_one(
        {"id_estacion": id_estacion},
        {
            "$set": {
                "precios_actuales": precios_update.precios.model_dump(),
                "fecha_actualizacion": datetime.now()
            },
            "$push": {
                "historico_precios": entrada_historial
            }
        }
    )
    
    if resultado.matched_count == 0:
        return None
    
    # Obtener y retornar la estación actualizada
    return await obtener_estacion_por_id(id_estacion)


async def eliminar_estacion(id_estacion: int) -> bool:
    """
    Elimina una estación de la base de datos
    
    Args:
        id_estacion: ID de la estación a eliminar
        
    Returns:
        True si se eliminó exitosamente, False si no existe
    """
    resultado = await estaciones_collection.delete_one({"id_estacion": id_estacion})
    return resultado.deleted_count > 0


async def obtener_historico_precios(id_estacion: int) -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene el historial de precios de una estación
    
    Args:
        id_estacion: ID de la estación
        
    Returns:
        Lista con el historial de precios o None si la estación no existe
    """
    estacion = await estaciones_collection.find_one(
        {"id_estacion": id_estacion},
        {"historico_precios": 1, "_id": 0}
    )
    
    if not estacion:
        return None
    
    return estacion.get("historico_precios", [])


async def verificar_ip_existente(ip: str, excluir_id: Optional[int] = None) -> bool:
    """
    Verifica si ya existe una estación con la IP especificada
    Útil para validación antes de crear/actualizar
    
    Args:
        ip: Dirección IP a verificar
        excluir_id: ID de estación a excluir de la búsqueda (útil al actualizar)
        
    Returns:
        True si la IP ya existe, False si está disponible
    """
    query = {"ip": ip}
    if excluir_id is not None:
        query["id_estacion"] = {"$ne": excluir_id}
    
    estacion = await estaciones_collection.find_one(query)
    return estacion is not None


async def obtener_estadisticas() -> Dict[str, Any]:
    """
    Obtiene estadísticas generales del sistema
    
    Returns:
        Diccionario con estadísticas: total estaciones, activas, inactivas, etc.
    """
    total = await estaciones_collection.count_documents({})
    activas = await estaciones_collection.count_documents({"estado": "Activa"})
    inactivas = await estaciones_collection.count_documents({"estado": "Inactiva"})
    desconectadas = await estaciones_collection.count_documents({"estado": "Desconectada"})
    
    return {
        "total_estaciones": total,
        "activas": activas,
        "inactivas": inactivas,
        "desconectadas": desconectadas
    }
