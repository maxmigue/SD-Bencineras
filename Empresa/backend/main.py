from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import subprocess
from typing import List, Dict, Any

# Importar modelos y servicios
from models import (
    EstacionCreate, 
    EstacionUpdate, 
    PreciosUpdate,
    EstacionResponse
)
from estaciones_service import (
    crear_estacion,
    obtener_estaciones,
    obtener_estacion_por_id,
    actualizar_estacion,
    actualizar_precios,
    eliminar_estacion,
    obtener_historico_precios,
    verificar_ip_existente,
    obtener_estadisticas
)
from database import verificar_conexion, cerrar_conexion
from tcp_server import iniciar_tcp_servidor

app = FastAPI(
    title="Backend Empresa Bencinera",
    version="1.0",
    description="API REST para gestión de estaciones de servicio"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def iniciar_componentes():
    # 🔹 Verificar conexión a MongoDB
    conexion_ok = await verificar_conexion()
    if not conexion_ok:
        print("⚠️ Advertencia: No se pudo conectar a MongoDB")
    
    # 🔹 Iniciar el servidor TCP en paralelo
    asyncio.create_task(iniciar_tcp_servidor())
    print("🚀 Servidor TCP iniciado junto con FastAPI")

    # 🔹 (Opcional) Iniciar el bridge Node.js automáticamente
    try:
        subprocess.Popen(["node", "tcp_bridge.js"], cwd=".", shell=True)
        print("🌐 Bridge Node.js iniciado correctamente")
    except Exception as e:
        print("⚠️ No se pudo iniciar el bridge:", e)

@app.on_event("shutdown")
async def cerrar_componentes():
    # 🔹 Cerrar conexión a MongoDB
    await cerrar_conexion()

@app.get("/")
def home():
    return {
        "status": "ok", 
        "message": "Backend Empresa Bencinera funcionando correctamente",
        "version": "2.0"
    }


# ============================================
# ENDPOINTS CRUD DE ESTACIONES
# ============================================

@app.get("/api/estaciones", response_model=List[Dict[str, Any]])
async def listar_estaciones():
    """
    Obtiene todas las estaciones registradas en el sistema
    """
    try:
        estaciones = await obtener_estaciones()
        return estaciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estaciones: {str(e)}"
        )


@app.get("/api/estaciones/{id_estacion}", response_model=Dict[str, Any])
async def obtener_estacion(id_estacion: int):
    """
    Obtiene los detalles de una estación específica por su ID
    """
    estacion = await obtener_estacion_por_id(id_estacion)
    
    if not estacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estación con ID {id_estacion} no encontrada"
        )
    
    return estacion


@app.post("/api/estaciones", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def crear_nueva_estacion(estacion: EstacionCreate):
    """
    Crea una nueva estación en el sistema
    
    - Valida que la IP no esté duplicada
    - Genera un ID único automáticamente
    - Agrega los precios iniciales al historial
    """
    try:
        # Validar que la IP no exista
        if await verificar_ip_existente(estacion.ip):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una estación con la IP {estacion.ip}"
            )
        
        estacion_creada = await crear_estacion(estacion)
        return estacion_creada
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear estación: {str(e)}"
        )


@app.put("/api/estaciones/{id_estacion}", response_model=Dict[str, Any])
async def actualizar_datos_estacion(id_estacion: int, datos: EstacionUpdate):
    """
    Actualiza los datos generales de una estación (nombre, IP, puerto, estado)
    
    Para actualizar precios, usar el endpoint /api/estaciones/{id}/precios
    """
    try:
        # Si se está actualizando la IP, validar que no exista
        if datos.ip is not None:
            if await verificar_ip_existente(datos.ip, excluir_id=id_estacion):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra estación con la IP {datos.ip}"
                )
        
        estacion_actualizada = await actualizar_estacion(id_estacion, datos)
        
        if not estacion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estación con ID {id_estacion} no encontrada"
            )
        
        return estacion_actualizada
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estación: {str(e)}"
        )


@app.delete("/api/estaciones/{id_estacion}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_estacion_endpoint(id_estacion: int):
    """
    Elimina una estación del sistema
    """
    try:
        eliminada = await eliminar_estacion(id_estacion)
        
        if not eliminada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estación con ID {id_estacion} no encontrada"
            )
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar estación: {str(e)}"
        )


@app.put("/api/estaciones/{id_estacion}/precios", response_model=Dict[str, Any])
async def actualizar_precios_estacion(id_estacion: int, precios: PreciosUpdate):
    """
    Actualiza los precios de una estación
    
    - Actualiza los precios actuales
    - Agrega una entrada al historial con timestamp
    - Distribuye los nuevos precios a la estación (Fase 5)
    """
    try:
        estacion_actualizada = await actualizar_precios(id_estacion, precios)
        
        if not estacion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estación con ID {id_estacion} no encontrada"
            )
        
        # TODO: Fase 5 - Enviar precios a la estación vía TCP
        # await enviar_precios_a_estacion(
        #     estacion_actualizada["ip"],
        #     estacion_actualizada["puerto"],
        #     precios.precios.model_dump()
        # )
        
        return estacion_actualizada
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar precios: {str(e)}"
        )


@app.get("/api/estaciones/{id_estacion}/historico", response_model=List[Dict[str, Any]])
async def obtener_historico(id_estacion: int):
    """
    Obtiene el historial de precios de una estación
    
    Retorna una lista ordenada cronológicamente con todos los cambios de precios
    """
    try:
        historico = await obtener_historico_precios(id_estacion)
        
        if historico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estación con ID {id_estacion} no encontrada"
            )
        
        return historico
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


@app.get("/api/estadisticas", response_model=Dict[str, Any])
async def obtener_estadisticas_sistema():
    """
    Obtiene estadísticas generales del sistema
    
    Retorna el total de estaciones y su distribución por estado
    """
    try:
        estadisticas = await obtener_estadisticas()
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
