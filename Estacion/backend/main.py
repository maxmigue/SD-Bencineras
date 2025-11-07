from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List
from datetime import datetime
from tcp_server import iniciar_tcp_servidor, obtener_precios_actuales, obtener_nombre_estacion
from database import conectar_db, desconectar_db, obtener_database
from models import (
    TransaccionCreate, 
    TransaccionResponse, 
    TransaccionDB,
    EstadoEstacion,
    PreciosModel
)

app = FastAPI(
    title="Backend Estación",
    version="1.0",
    description="API para gestión de transacciones y surtidores en la estación"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def iniciar_componentes():
    # 🔹 Conectar a MongoDB
    await conectar_db()
    
    # 🔹 Iniciar el servidor TCP en paralelo
    asyncio.create_task(iniciar_tcp_servidor())
    print("🚀 Servidor TCP iniciado junto con FastAPI")


@app.on_event("shutdown")
async def cerrar_componentes():
    await desconectar_db()


@app.get("/")
def home():
    return {"status": "ok", "message": "Backend Estación funcionando correctamente"}


@app.get("/estado", response_model=EstadoEstacion)
async def obtener_estado():
    """
    Obtiene el estado general de la estación
    """
    try:
        db = obtener_database()
        
        # Obtener nombre de la estación (puede venir de Empresa o variable de entorno)
        nombre = obtener_nombre_estacion()
        
        # Obtener precios actuales
        precios = obtener_precios_actuales()
        
        # Calcular estadísticas de transacciones
        total_transacciones = await db.transacciones.count_documents({})
        
        # Calcular ingresos totales
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$monto_total"}}}
        ]
        resultado = await db.transacciones.aggregate(pipeline).to_list(1)
        ingresos_totales = resultado[0]["total"] if resultado else 0
        
        return EstadoEstacion(
            nombre=nombre,
            precios=PreciosModel(**precios),
            total_transacciones=total_transacciones,
            ingresos_totales=ingresos_totales,
            estado="activa"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )


@app.get("/precios", response_model=PreciosModel)
def obtener_precios():
    """
    Obtiene los precios actuales de combustibles
    """
    precios = obtener_precios_actuales()
    return PreciosModel(**precios)


@app.post("/transacciones", response_model=TransaccionResponse, status_code=status.HTTP_201_CREATED)
async def crear_transaccion(transaccion: TransaccionCreate):
    """
    Registra una nueva transacción
    """
    try:
        db = obtener_database()
        
        # Crear documento de transacción
        transaccion_db = TransaccionDB(**transaccion.model_dump())
        transaccion_dict = transaccion_db.model_dump()
        
        # Insertar en la base de datos
        resultado = await db.transacciones.insert_one(transaccion_dict)
        
        # Obtener la transacción insertada
        transaccion_insertada = await db.transacciones.find_one({"_id": resultado.inserted_id})
        
        if transaccion_insertada:
            transaccion_insertada["_id"] = str(transaccion_insertada["_id"])
            return TransaccionResponse(**transaccion_insertada)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al recuperar la transacción creada"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando transacción: {str(e)}"
        )


@app.get("/transacciones", response_model=List[TransaccionResponse])
async def listar_transacciones(
    limit: int = 100,
    skip: int = 0,
    surtidor_id: str = None,
    tipo_combustible: str = None
):
    """
    Lista las transacciones con filtros opcionales
    """
    try:
        db = obtener_database()
        
        # Construir filtro
        filtro = {}
        if surtidor_id:
            filtro["surtidor_id"] = surtidor_id
        if tipo_combustible:
            filtro["tipo_combustible"] = tipo_combustible
        
        # Obtener transacciones
        cursor = db.transacciones.find(filtro).sort("fecha", -1).skip(skip).limit(limit)
        transacciones = await cursor.to_list(length=limit)
        
        # Convertir ObjectId a string
        for t in transacciones:
            t["_id"] = str(t["_id"])
        
        return [TransaccionResponse(**t) for t in transacciones]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando transacciones: {str(e)}"
        )


@app.get("/transacciones/{transaccion_id}", response_model=TransaccionResponse)
async def obtener_transaccion(transaccion_id: str):
    """
    Obtiene una transacción específica por ID
    """
    try:
        from bson import ObjectId
        db = obtener_database()
        
        transaccion = await db.transacciones.find_one({"_id": ObjectId(transaccion_id)})
        
        if not transaccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transacción {transaccion_id} no encontrada"
            )
        
        transaccion["_id"] = str(transaccion["_id"])
        return TransaccionResponse(**transaccion)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo transacción: {str(e)}"
        )
