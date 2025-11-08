# Guía de Desarrollo: Integración de Surtidores con Estación

## 📋 Especificaciones del Sistema

Basado en los requerimientos clarificados:

1. ✅ **Arquitectura**: Contenedores separados que se conectan a la Estación por TCP
2. ✅ **Frontend**: Cada surtidor mantiene su propio frontend Next.js
3. ✅ **Gestión**: Los surtidores se configuran en la BD y se levantan con docker-compose
4. ✅ **Servicios**: Mantener FastAPI en cada surtidor
5. ✅ **CRUD**: Registrar/configurar surtidores en la BD de la Estación
6. ✅ **Transacciones**: Iniciadas desde el frontend del surtidor, enviadas al completar

---

## 🏗️ Arquitectura Final

```
┌────────────────────────────────────────────────────────────┐
│                        EMPRESA                              │
│  - Actualiza precios globalmente                           │
└────────────────┬───────────────────────────────────────────┘
                 │ TCP (puerto 5001)
                 │ Actualización de precios
                 ▼
┌────────────────────────────────────────────────────────────┐
│                       ESTACIÓN                              │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Backend FastAPI (puerto 8001)                    │     │
│  │  - CRUD de Surtidores                            │     │
│  │  - Recibe/guarda transacciones                   │     │
│  │  - Gestiona estados de surtidores                │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │ TCP Server Surtidores (puerto 6000)              │     │
│  │  - Escucha conexiones de surtidores              │     │
│  │  - Propaga precios actualizados                  │     │
│  │  - Recibe transacciones completadas              │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │ MongoDB (puerto 27018)                           │     │
│  │  Colecciones:                                    │     │
│  │   - transacciones                                │     │
│  │   - surtidores (config + metadata)               │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Frontend Next.js (puerto 3001)                   │     │
│  │  - Panel de control de la estación               │     │
│  │  - Vista de surtidores y transacciones           │     │
│  │  - CRUD de surtidores                            │     │
│  └──────────────────────────────────────────────────┘     │
└────────────┬───────────────┬──────────────┬───────────────┘
             │               │              │
             │ TCP 6000      │ TCP 6000     │ TCP 6000
             ▼               ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ SURTIDOR 1   │ │ SURTIDOR 2   │ │ SURTIDOR N   │
     │ (Container)  │ │ (Container)  │ │ (Container)  │
     │              │ │              │ │              │
     │ Backend:8002 │ │ Backend:8003 │ │ Backend:800N │
     │ Frontend:3002│ │ Frontend:3003│ │ Frontend:300N│
     │              │ │              │ │              │
     │ TCP Client   │ │ TCP Client   │ │ TCP Client   │
     │ → Estación   │ │ → Estación   │ │ → Estación   │
     └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📊 Modelos de Datos (Estación)

### Archivo: `Estacion/backend/models.py` (agregar)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================
# MODELOS DE SURTIDORES
# ============================================

class SurtidorCreate(BaseModel):
    """Modelo para registrar un nuevo surtidor"""
    nombre: str = Field(..., description="Nombre del surtidor", min_length=3)
    combustibles_soportados: List[str] = Field(
        default=["93", "95", "97", "diesel"],
        description="Tipos de combustible soportados"
    )
    combustible_actual: str = Field(
        default="95",
        description="Tipo de combustible configurado actualmente"
    )
    capacidad_maxima: float = Field(
        default=100.0,
        ge=0,
        description="Capacidad máxima en litros"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Surtidor Norte 1",
                "combustibles_soportados": ["93", "95", "97", "diesel"],
                "combustible_actual": "95",
                "capacidad_maxima": 100.0
            }
        }


class SurtidorUpdate(BaseModel):
    """Modelo para actualizar configuración de surtidor"""
    nombre: Optional[str] = None
    combustible_actual: Optional[str] = None
    capacidad_maxima: Optional[float] = None
    estado: Optional[str] = None  # disponible, fuera_servicio, mantenimiento


class SurtidorResponse(BaseModel):
    """Modelo de respuesta con datos del surtidor"""
    id: str = Field(alias="_id")
    id_surtidor: int
    nombre: str
    estado: str  # disponible, ocupado, fuera_servicio, desconectado
    estado_conexion: str  # conectado, desconectado
    combustibles_soportados: List[str]
    combustible_actual: str
    capacidad_maxima: float
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    ultima_conexion: Optional[datetime] = None
    
    # Estadísticas
    total_transacciones: int = 0
    litros_totales: float = 0.0
    ingresos_totales: int = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class SurtidorDB(BaseModel):
    """Modelo interno para MongoDB"""
    id_surtidor: int
    nombre: str
    estado: str = "disponible"
    estado_conexion: str = "desconectado"
    combustibles_soportados: List[str]
    combustible_actual: str
    capacidad_maxima: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    ultima_conexion: Optional[datetime] = None
    
    # Estadísticas (actualizadas en cada transacción)
    total_transacciones: int = 0
    litros_totales: float = 0.0
    ingresos_totales: int = 0


class EstadoSurtidorTiempoReal(BaseModel):
    """Estado del surtidor en tiempo real (en memoria/cache)"""
    id_surtidor: int
    estado_conexion: str  # conectado, desconectado
    estado_operacion: str  # disponible, despachando, pausado
    litros_actuales: float = 0.0
    monto_actual: int = 0
    tipo_combustible: str
    precio_por_litro: int
    timestamp: datetime = Field(default_factory=datetime.now)
```

---

## 🔧 Servicios CRUD (Estación)

### Archivo: `Estacion/backend/surtidores_service.py` (NUEVO)

```python
"""
Servicios de gestión de surtidores
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import SurtidorCreate, SurtidorUpdate, SurtidorDB
from database import obtener_database
from bson import ObjectId


async def crear_surtidor(surtidor: SurtidorCreate) -> Dict[str, Any]:
    """
    Crea un nuevo surtidor en la base de datos
    
    Args:
        surtidor: Datos del surtidor a crear
        
    Returns:
        Diccionario con los datos del surtidor creado
    """
    db = obtener_database()
    
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
    cursor = db.surtidores.find()
    
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
    
    if not datos_actualizacion:
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
    cursor = db.surtidores.find({"estado_conexion": "conectado"})
    
    async for surtidor in cursor:
        surtidor["_id"] = str(surtidor["_id"])
        surtidores.append(surtidor)
    
    return surtidores
```

---

## 🌐 Servidor TCP para Surtidores (Estación)

### Archivo: `Estacion/backend/tcp_server_surtidores.py` (NUEVO)

```python
"""
Servidor TCP para manejar conexiones de surtidores
Puerto: 6000 (diferente al 5000 que usa para recibir de Empresa)
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from database import obtener_database
from surtidores_service import (
    actualizar_conexion_surtidor,
    actualizar_estadisticas_surtidor,
    obtener_surtidor_por_id
)
from tcp_server import obtener_precios_actuales

# Diccionario de surtidores conectados: {id_surtidor: writer}
surtidores_conectados: Dict[int, asyncio.StreamWriter] = {}

# Set de writers para envío de mensajes broadcast
clientes_surtidores: Set[asyncio.StreamWriter] = set()


async def manejar_conexion_surtidor(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Maneja la conexión de un surtidor individual
    """
    addr = writer.get_extra_info('peername')
    id_surtidor = None
    
    try:
        print(f"🔌 Nueva conexión desde {addr}")
        
        # Esperar mensaje de registro
        registro_data = await asyncio.wait_for(reader.readline(), timeout=10.0)
        
        if not registro_data:
            print(f"⚠️ Conexión cerrada sin registro desde {addr}")
            return
        
        registro = json.loads(registro_data.decode())
        
        if registro.get("tipo") != "registro":
            print(f"⚠️ Primer mensaje no es registro: {registro}")
            writer.close()
            await writer.wait_closed()
            return
        
        id_surtidor = registro.get("id_surtidor")
        
        if not id_surtidor:
            print(f"⚠️ Registro sin id_surtidor: {registro}")
            writer.close()
            await writer.wait_closed()
            return
        
        # Verificar que el surtidor existe en la BD
        surtidor = await obtener_surtidor_por_id(id_surtidor)
        
        if not surtidor:
            print(f"❌ Surtidor {id_surtidor} no registrado en la BD")
            # Enviar error
            error_msg = {
                "tipo": "error",
                "codigo": "SURTIDOR_NO_REGISTRADO",
                "mensaje": f"Surtidor {id_surtidor} no existe. Registrarlo primero."
            }
            writer.write((json.dumps(error_msg) + "\n").encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        
        print(f"✅ Surtidor {id_surtidor} ({surtidor['nombre']}) registrado")
        
        # Registrar conexión
        surtidores_conectados[id_surtidor] = writer
        clientes_surtidores.add(writer)
        await actualizar_conexion_surtidor(id_surtidor, "conectado")
        
        # Enviar confirmación con precios actuales
        precios = obtener_precios_actuales()
        confirmacion = {
            "tipo": "registro_confirmado",
            "id_surtidor": id_surtidor,
            "mensaje": "Surtidor registrado exitosamente",
            "precios": precios
        }
        writer.write((json.dumps(confirmacion) + "\n").encode())
        await writer.drain()
        
        # Loop principal: recibir mensajes del surtidor
        last_heartbeat = datetime.now()
        
        while True:
            try:
                # Timeout de 90 segundos (esperamos heartbeat cada 30s)
                data = await asyncio.wait_for(reader.readline(), timeout=90.0)
                
                if not data:
                    print(f"⚠️ Conexión cerrada por surtidor {id_surtidor}")
                    break
                
                mensaje = json.loads(data.decode())
                last_heartbeat = datetime.now()
                
                # Procesar mensaje
                await procesar_mensaje_surtidor(id_surtidor, mensaje)
                
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout: Surtidor {id_surtidor} sin heartbeat")
                break
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON inválido desde surtidor {id_surtidor}: {e}")
            except Exception as e:
                print(f"❌ Error procesando mensaje de surtidor {id_surtidor}: {e}")
                break
    
    except asyncio.TimeoutError:
        print(f"⏱️ Timeout esperando registro desde {addr}")
    except Exception as e:
        print(f"❌ Error en conexión desde {addr}: {e}")
    finally:
        # Limpiar conexión
        if id_surtidor:
            print(f"❌ Surtidor {id_surtidor} desconectado")
            surtidores_conectados.pop(id_surtidor, None)
            await actualizar_conexion_surtidor(id_surtidor, "desconectado")
        
        clientes_surtidores.discard(writer)
        writer.close()
        await writer.wait_closed()


async def procesar_mensaje_surtidor(id_surtidor: int, mensaje: dict):
    """
    Procesa diferentes tipos de mensajes recibidos de un surtidor
    """
    tipo = mensaje.get("tipo")
    
    if tipo == "estado":
        # Actualización de estado en tiempo real
        print(f"📊 Estado surtidor {id_surtidor}: {mensaje.get('estado_operacion')}")
        # Aquí puedes actualizar un cache en memoria o Redis si es necesario
        
    elif tipo == "transaccion_completada":
        # Guardar transacción en la BD
        await guardar_transaccion(id_surtidor, mensaje)
        
    elif tipo == "heartbeat":
        # Simplemente mantener la conexión viva
        pass
        
    elif tipo == "error":
        print(f"🚨 Error en surtidor {id_surtidor}: {mensaje.get('mensaje')}")
        # Registrar error, enviar notificación, etc.
        
    else:
        print(f"⚠️ Tipo de mensaje desconocido: {tipo}")


async def guardar_transaccion(id_surtidor: int, datos: dict):
    """
    Guarda una transacción completada en la base de datos
    """
    try:
        db = obtener_database()
        
        # Obtener datos del surtidor
        surtidor = await obtener_surtidor_por_id(id_surtidor)
        
        transaccion = {
            "surtidor_id": str(id_surtidor),
            "nombre_surtidor": surtidor["nombre"] if surtidor else f"Surtidor {id_surtidor}",
            "tipo_combustible": datos.get("tipo_combustible"),
            "litros": datos.get("litros"),
            "precio_por_litro": datos.get("precio_por_litro"),
            "monto_total": datos.get("monto_total"),
            "metodo_pago": datos.get("metodo_pago", "efectivo"),
            "fecha": datetime.fromisoformat(datos.get("fecha_fin")) if datos.get("fecha_fin") else datetime.now(),
            "estado": "completada"
        }
        
        # Insertar transacción
        resultado = await db.transacciones.insert_one(transaccion)
        
        # Actualizar estadísticas del surtidor
        await actualizar_estadisticas_surtidor(
            id_surtidor,
            datos.get("litros", 0),
            datos.get("monto_total", 0)
        )
        
        print(f"✅ Transacción guardada: {resultado.inserted_id}")
        
    except Exception as e:
        print(f"❌ Error guardando transacción: {e}")


async def propagar_precios_a_surtidores(nuevos_precios: dict):
    """
    Propaga actualización de precios a todos los surtidores conectados
    
    Args:
        nuevos_precios: Diccionario con los nuevos precios
    """
    mensaje = {
        "tipo": "actualizacion_precios",
        "precios": nuevos_precios,
        "timestamp": datetime.now().isoformat()
    }
    
    data = (json.dumps(mensaje) + "\n").encode()
    
    desconectados = []
    
    for id_surtidor, writer in surtidores_conectados.items():
        try:
            writer.write(data)
            await writer.drain()
            print(f"📤 Precios enviados a surtidor {id_surtidor}")
        except Exception as e:
            print(f"❌ Error enviando precios a surtidor {id_surtidor}: {e}")
            desconectados.append(id_surtidor)
    
    # Limpiar conexiones muertas
    for id_surtidor in desconectados:
        surtidores_conectados.pop(id_surtidor, None)
        await actualizar_conexion_surtidor(id_surtidor, "desconectado")


async def iniciar_servidor_tcp_surtidores():
    """
    Inicia el servidor TCP para escuchar conexiones de surtidores
    """
    server = await asyncio.start_server(
        manejar_conexion_surtidor,
        "0.0.0.0",
        6000
    )
    
    print("🟢 Servidor TCP Surtidores escuchando en 0.0.0.0:6000")
    
    async with server:
        await server.serve_forever()


def obtener_surtidores_activos() -> Dict[int, asyncio.StreamWriter]:
    """
    Retorna el diccionario de surtidores actualmente conectados
    """
    return surtidores_conectados.copy()
```

---

## 🔄 Integración con tcp_server.py existente (Estación)

### Modificar: `Estacion/backend/tcp_server.py`

Agregar al final del archivo la propagación a surtidores cuando llegan precios de Empresa:

```python
# ... código existente ...

async def manejar_surtidor(reader, writer):
    # ... código existente que maneja conexiones de Empresa ...
    
    # AGREGAR después de actualizar precios_actuales:
    if mensaje.get("tipo") == "actualizacion_precios":
        # ... código existente ...
        precios_actuales.update(nuevos_precios)
        
        # 🆕 NUEVO: Propagar a surtidores
        from tcp_server_surtidores import propagar_precios_a_surtidores
        await propagar_precios_a_surtidores(precios_actuales)
```

---

## 🚀 Endpoints API REST (Estación)

### Modificar: `Estacion/backend/main.py`

```python
# ... imports existentes ...
from surtidores_service import (
    crear_surtidor,
    obtener_surtidores,
    obtener_surtidor_por_id,
    actualizar_surtidor,
    eliminar_surtidor,
    verificar_nombre_existente,
    obtener_surtidores_conectados
)
from tcp_server_surtidores import iniciar_servidor_tcp_surtidores
from models import SurtidorCreate, SurtidorUpdate, SurtidorResponse

# ... código existente ...

@app.on_event("startup")
async def iniciar_componentes():
    # 🔹 Conectar a MongoDB
    await conectar_db()
    
    # 🔹 Iniciar servidor TCP para Empresa (existente)
    asyncio.create_task(iniciar_tcp_servidor())
    
    # 🔹 🆕 NUEVO: Iniciar servidor TCP para Surtidores
    asyncio.create_task(iniciar_servidor_tcp_surtidores())
    print("🚀 Servidor TCP Surtidores iniciado")


# ============================================
# 🆕 NUEVOS ENDPOINTS - CRUD DE SURTIDORES
# ============================================

@app.get("/api/surtidores", response_model=List[Dict[str, Any]])
async def listar_surtidores():
    """Lista todos los surtidores registrados"""
    try:
        surtidores = await obtener_surtidores()
        return surtidores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener surtidores: {str(e)}"
        )


@app.get("/api/surtidores/conectados", response_model=List[Dict[str, Any]])
async def listar_surtidores_conectados():
    """Lista solo los surtidores actualmente conectados"""
    try:
        surtidores = await obtener_surtidores_conectados()
        return surtidores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener surtidores conectados: {str(e)}"
        )


@app.get("/api/surtidores/{id_surtidor}", response_model=Dict[str, Any])
async def obtener_surtidor(id_surtidor: int):
    """Obtiene detalles de un surtidor específico"""
    surtidor = await obtener_surtidor_por_id(id_surtidor)
    
    if not surtidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surtidor {id_surtidor} no encontrado"
        )
    
    return surtidor


@app.post("/api/surtidores", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def registrar_surtidor(surtidor: SurtidorCreate):
    """Registra un nuevo surtidor en el sistema"""
    try:
        # Verificar nombre duplicado
        existe = await verificar_nombre_existente(surtidor.nombre)
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un surtidor con el nombre '{surtidor.nombre}'"
            )
        
        surtidor_creado = await crear_surtidor(surtidor)
        return surtidor_creado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando surtidor: {str(e)}"
        )


@app.put("/api/surtidores/{id_surtidor}", response_model=Dict[str, Any])
async def actualizar_config_surtidor(id_surtidor: int, datos: SurtidorUpdate):
    """Actualiza la configuración de un surtidor"""
    try:
        # Verificar nombre duplicado si se está cambiando
        if datos.nombre:
            existe = await verificar_nombre_existente(datos.nombre, excluir_id=id_surtidor)
            if existe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro surtidor con el nombre '{datos.nombre}'"
                )
        
        surtidor_actualizado = await actualizar_surtidor(id_surtidor, datos)
        
        if not surtidor_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surtidor {id_surtidor} no encontrado"
            )
        
        return surtidor_actualizado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando surtidor: {str(e)}"
        )


@app.delete("/api/surtidores/{id_surtidor}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_surtidor_endpoint(id_surtidor: int):
    """Elimina un surtidor del sistema"""
    try:
        eliminado = await eliminar_surtidor(id_surtidor)
        
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surtidor {id_surtidor} no encontrado"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando surtidor: {str(e)}"
        )


@app.get("/api/surtidores/{id_surtidor}/transacciones", response_model=List[TransaccionResponse])
async def listar_transacciones_surtidor(
    id_surtidor: int,
    limit: int = 50,
    skip: int = 0
):
    """Lista las transacciones de un surtidor específico"""
    try:
        # Verificar que el surtidor existe
        surtidor = await obtener_surtidor_por_id(id_surtidor)
        if not surtidor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surtidor {id_surtidor} no encontrado"
            )
        
        db = obtener_database()
        cursor = db.transacciones.find(
            {"surtidor_id": str(id_surtidor)}
        ).sort("fecha", -1).skip(skip).limit(limit)
        
        transacciones = await cursor.to_list(length=limit)
        
        for t in transacciones:
            t["_id"] = str(t["_id"])
        
        return [TransaccionResponse(**t) for t in transacciones]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando transacciones: {str(e)}"
        )
```

---

## 🔌 Cliente TCP del Surtidor

### Modificar: `Surtidor/backend/main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from datetime import datetime

# --- Configuración ---
ESTACION_HOST = os.getenv("ESTACION_HOST", "estacion-backend")  # nombre del contenedor
ESTACION_PORT = int(os.getenv("ESTACION_PORT", "6000"))
ID_SURTIDOR = int(os.getenv("ID_SURTIDOR", "1"))
NOMBRE_SURTIDOR = os.getenv("NOMBRE_SURTIDOR", f"Surtidor {ID_SURTIDOR}")

# --- Estado del Surtidor ---
surtidor = {
    "id_surtidor": ID_SURTIDOR,
    "nombre": NOMBRE_SURTIDOR,
    "estado_operacion": "disponible",  # disponible, despachando, pausado
    "tipo_combustible": "95",
    "litros_actuales": 0.0,
    "monto_actual": 0,
    "precio_litro": 1350,
    "combustibles_soportados": ["93", "95", "97", "diesel"]
}

# Precios actuales (actualizados por la estación)
precios = {
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
}

# Writer global para enviar mensajes a la estación
writer_estacion = None

# --- FastAPI ---
app = FastAPI(
    title="API del Surtidor",
    description="Backend individual de un surtidor",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# CLIENTE TCP - CONEXIÓN CON ESTACIÓN
# ============================================

async def conectar_a_estacion():
    """Cliente TCP con reconexión automática"""
    global writer_estacion
    
    while True:
        try:
            reader, writer = await asyncio.open_connection(ESTACION_HOST, ESTACION_PORT)
            writer_estacion = writer
            print(f"✅ Conectado a estación en {ESTACION_HOST}:{ESTACION_PORT}")
            
            # Enviar mensaje de registro
            await enviar_registro()
            
            # Loop de recepción de mensajes
            while True:
                data = await reader.readline()
                
                if not data:
                    print("⚠️ Conexión cerrada por la estación")
                    break
                
                try:
                    mensaje = json.loads(data.decode())
                    await procesar_mensaje_estacion(mensaje)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON inválido: {e}")
                    
        except ConnectionRefusedError:
            print(f"🔌 No se pudo conectar a estación. Reintentando en 5s...")
            writer_estacion = None
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
            writer_estacion = None
        
        await asyncio.sleep(5)


async def enviar_registro():
    """Envía mensaje de registro inicial"""
    if writer_estacion:
        try:
            registro = {
                "tipo": "registro",
                "id_surtidor": ID_SURTIDOR,
                "nombre": NOMBRE_SURTIDOR,
                "combustibles_soportados": surtidor["combustibles_soportados"],
                "version": "1.0"
            }
            data = (json.dumps(registro) + "\n").encode()
            writer_estacion.write(data)
            await writer_estacion.drain()
            print(f"📤 Registro enviado: {registro}")
        except Exception as e:
            print(f"❌ Error enviando registro: {e}")


async def procesar_mensaje_estacion(mensaje: dict):
    """Procesa mensajes recibidos de la estación"""
    tipo = mensaje.get("tipo")
    
    if tipo == "registro_confirmado":
        print(f"✅ Registro confirmado: {mensaje.get('mensaje')}")
        # Actualizar precios
        nuevos_precios = mensaje.get("precios", {})
        precios.update(nuevos_precios)
        actualizar_precio_actual()
        
    elif tipo == "actualizacion_precios":
        print(f"💰 Actualización de precios recibida")
        nuevos_precios = mensaje.get("precios", {})
        precios.update(nuevos_precios)
        actualizar_precio_actual()
        
    elif tipo == "comando":
        comando = mensaje.get("comando")
        print(f"🎮 Comando recibido: {comando}")
        # Implementar lógica de comandos (pausar, reanudar, etc.)
        
    elif tipo == "error":
        print(f"🚨 Error desde estación: {mensaje.get('mensaje')}")


def actualizar_precio_actual():
    """Actualiza el precio actual según el combustible configurado"""
    tipo = surtidor["tipo_combustible"]
    if tipo == "93":
        surtidor["precio_litro"] = precios["precio_93"]
    elif tipo == "95":
        surtidor["precio_litro"] = precios["precio_95"]
    elif tipo == "97":
        surtidor["precio_litro"] = precios["precio_97"]
    elif tipo == "diesel":
        surtidor["precio_litro"] = precios["precio_diesel"]
    print(f"💰 Precio actualizado: ${surtidor['precio_litro']}/L")


async def enviar_estado():
    """Envía el estado actual a la estación"""
    if writer_estacion:
        try:
            estado = {
                "tipo": "estado",
                "id_surtidor": ID_SURTIDOR,
                "estado_operacion": surtidor["estado_operacion"],
                "litros_actuales": surtidor["litros_actuales"],
                "monto_actual": surtidor["monto_actual"],
                "tipo_combustible": surtidor["tipo_combustible"],
                "timestamp": datetime.now().isoformat()
            }
            data = (json.dumps(estado) + "\n").encode()
            writer_estacion.write(data)
            await writer_estacion.drain()
        except Exception as e:
            print(f"❌ Error enviando estado: {e}")


async def enviar_transaccion_completada(transaccion_data: dict):
    """Envía una transacción completada a la estación"""
    if writer_estacion:
        try:
            mensaje = {
                "tipo": "transaccion_completada",
                "id_surtidor": ID_SURTIDOR,
                "tipo_combustible": transaccion_data["tipo_combustible"],
                "litros": transaccion_data["litros"],
                "precio_por_litro": transaccion_data["precio_por_litro"],
                "monto_total": transaccion_data["monto_total"],
                "metodo_pago": transaccion_data["metodo_pago"],
                "fecha_inicio": transaccion_data["fecha_inicio"],
                "fecha_fin": datetime.now().isoformat()
            }
            data = (json.dumps(mensaje) + "\n").encode()
            writer_estacion.write(data)
            await writer_estacion.drain()
            print(f"✅ Transacción enviada a estación")
        except Exception as e:
            print(f"❌ Error enviando transacción: {e}")


async def heartbeat_task():
    """Envía heartbeat cada 30 segundos"""
    while True:
        await asyncio.sleep(30)
        if writer_estacion:
            try:
                heartbeat = {
                    "tipo": "heartbeat",
                    "id_surtidor": ID_SURTIDOR,
                    "timestamp": datetime.now().isoformat()
                }
                data = (json.dumps(heartbeat) + "\n").encode()
                writer_estacion.write(data)
                await writer_estacion.drain()
            except Exception as e:
                print(f"⚠️ Error enviando heartbeat: {e}")


# ============================================
# SIMULACIÓN DE CARGA
# ============================================

async def simular_carga():
    """Simula el despacho de combustible"""
    while True:
        if surtidor["estado_operacion"] == "despachando":
            await asyncio.sleep(1)  # 1 litro por segundo
            surtidor["litros_actuales"] += 1.0
            surtidor["monto_actual"] = int(surtidor["litros_actuales"] * surtidor["precio_litro"])
            
            # Enviar estado actualizado cada 2 segundos
            if int(surtidor["litros_actuales"]) % 2 == 0:
                await enviar_estado()
        
        await asyncio.sleep(1)


# ============================================
# EVENTOS DE FASTAPI
# ============================================

@app.on_event("startup")
async def startup_event():
    # Iniciar conexión con estación
    asyncio.create_task(conectar_a_estacion())
    
    # Iniciar simulación de carga
    asyncio.create_task(simular_carga())
    
    # Iniciar heartbeat
    asyncio.create_task(heartbeat_task())


# ============================================
# ENDPOINTS
# ============================================

@app.get("/estado")
async def get_estado():
    """Obtiene el estado actual del surtidor"""
    return {
        **surtidor,
        "precios_disponibles": precios,
        "conectado_estacion": writer_estacion is not None
    }


@app.post("/control/iniciar-carga")
async def iniciar_carga():
    """Inicia la carga de combustible"""
    if surtidor["estado_operacion"] == "disponible":
        surtidor["estado_operacion"] = "despachando"
        surtidor["litros_actuales"] = 0.0
        surtidor["monto_actual"] = 0
        surtidor["fecha_inicio"] = datetime.now().isoformat()
        await enviar_estado()
        return {"mensaje": "Carga iniciada"}
    raise HTTPException(status_code=400, detail="El surtidor no está disponible.")


@app.post("/control/detener-carga")
async def detener_carga(metodo_pago: str = "efectivo"):
    """Detiene la carga y registra la transacción"""
    if surtidor["estado_operacion"] == "despachando":
        # Preparar datos de transacción
        transaccion = {
            "tipo_combustible": surtidor["tipo_combustible"],
            "litros": surtidor["litros_actuales"],
            "precio_por_litro": surtidor["precio_litro"],
            "monto_total": surtidor["monto_actual"],
            "metodo_pago": metodo_pago,
            "fecha_inicio": surtidor.get("fecha_inicio", datetime.now().isoformat())
        }
        
        # Cambiar estado
        surtidor["estado_operacion"] = "disponible"
        
        # Enviar transacción a la estación
        await enviar_transaccion_completada(transaccion)
        
        # Resetear valores
        resultado = {
            "mensaje": "Carga completada y transacción registrada",
            "litros": surtidor["litros_actuales"],
            "total": surtidor["monto_actual"]
        }
        
        surtidor["litros_actuales"] = 0.0
        surtidor["monto_actual"] = 0
        
        await enviar_estado()
        
        return resultado
    
    raise HTTPException(status_code=400, detail="El surtidor no está cargando.")


@app.put("/configuracion")
async def actualizar_configuracion(tipo_combustible: str = None):
    """Actualiza la configuración del surtidor"""
    if surtidor["estado_operacion"] == "despachando":
        raise HTTPException(
            status_code=400,
            detail="No se puede cambiar configuración durante despacho"
        )
    
    if tipo_combustible and tipo_combustible in surtidor["combustibles_soportados"]:
        surtidor["tipo_combustible"] = tipo_combustible
        actualizar_precio_actual()
        await enviar_estado()
        return {"mensaje": "Configuración actualizada", "estado": surtidor}
    
    raise HTTPException(status_code=400, detail="Tipo de combustible no válido")
```

---

## 📦 Docker Compose (Estación con Múltiples Surtidores)

### Archivo: `Estacion/docker-compose.yml` (ACTUALIZADO)

```yaml
version: '3.8'

services:
  # MongoDB - Base de datos de la estación
  mongodb:
    image: mongo:7.0
    container_name: estacion-mongodb
    restart: always
    ports:
      - "27018:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=estacion_db
    networks:
      - estacion-network

  # Backend de la Estación
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: estacion-backend
    restart: always
    ports:
      - "8001:8000"  # FastAPI
      - "5001:5000"  # TCP Server para Empresa
      - "6001:6000"  # TCP Server para Surtidores (NUEVO)
      - "4001:4000"  # WebSocket Bridge
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - DATABASE_NAME=estacion_db
      - BACKEND_PORT=8000
      - FRONTEND_URL=http://localhost:3001
    depends_on:
      - mongodb
    volumes:
      - ./backend:/app
      - /app/node_modules
      - /app/__pycache__
    networks:
      - estacion-network

  # Frontend de la Estación
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: estacion-frontend
    restart: always
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
      - NEXT_PUBLIC_WS_URL=http://localhost:4001
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    networks:
      - estacion-network

  # Surtidor 1
  surtidor1-backend:
    build:
      context: ../Surtidor/backend
      dockerfile: Dockerfile
    container_name: surtidor1-backend
    restart: always
    ports:
      - "8002:8000"
    environment:
      - ESTACION_HOST=estacion-backend
      - ESTACION_PORT=6000
      - ID_SURTIDOR=1
      - NOMBRE_SURTIDOR=Surtidor Norte 1
    depends_on:
      - backend
    networks:
      - estacion-network

  surtidor1-frontend:
    build:
      context: ../Surtidor/frontend
      dockerfile: Dockerfile
    container_name: surtidor1-frontend
    restart: always
    ports:
      - "3002:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8002
    depends_on:
      - surtidor1-backend
    networks:
      - estacion-network

  # Surtidor 2
  surtidor2-backend:
    build:
      context: ../Surtidor/backend
      dockerfile: Dockerfile
    container_name: surtidor2-backend
    restart: always
    ports:
      - "8003:8000"
    environment:
      - ESTACION_HOST=estacion-backend
      - ESTACION_PORT=6000
      - ID_SURTIDOR=2
      - NOMBRE_SURTIDOR=Surtidor Sur 1
    depends_on:
      - backend
    networks:
      - estacion-network

  surtidor2-frontend:
    build:
      context: ../Surtidor/frontend
      dockerfile: Dockerfile
    container_name: surtidor2-frontend
    restart: always
    ports:
      - "3003:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8003
    depends_on:
      - surtidor2-backend
    networks:
      - estacion-network

  # Agregar más surtidores según sea necesario...

networks:
  estacion-network:
    driver: bridge

volumes:
  mongodb_data:
    driver: local
```

---

## 🚀 Pasos de Implementación

### Fase 1: Preparar Modelos y Servicios (Estación)

1. ✅ Agregar modelos de surtidores en `Estacion/backend/models.py`
2. ✅ Crear `Estacion/backend/surtidores_service.py`
3. ✅ Actualizar `Estacion/backend/database.py` para crear índices de surtidores

### Fase 2: Servidor TCP para Surtidores (Estación)

4. ✅ Crear `Estacion/backend/tcp_server_surtidores.py`
5. ✅ Integrar con `tcp_server.py` para propagar precios
6. ✅ Actualizar `main.py` para iniciar el servidor TCP en el puerto 6000

### Fase 3: Endpoints API REST (Estación)

7. ✅ Agregar endpoints CRUD de surtidores en `main.py`
8. ✅ Probar endpoints con Postman/Thunder Client

### Fase 4: Cliente TCP del Surtidor

9. ✅ Actualizar `Surtidor/backend/main.py` con cliente TCP
10. ✅ Implementar envío de transacciones
11. ✅ Implementar heartbeat

### Fase 5: Docker Compose

12. ✅ Actualizar `Estacion/docker-compose.yml` para incluir surtidores
13. ✅ Configurar variables de entorno para cada surtidor
14. ✅ Exponer puertos necesarios

### Fase 6: Testing

15. ✅ Registrar surtidores en la BD usando API
16. ✅ Levantar surtidores con docker-compose
17. ✅ Verificar conexión TCP
18. ✅ Probar actualización de precios (Empresa → Estación → Surtidores)
19. ✅ Probar transacciones (Surtidor → Estación)
20. ✅ Verificar persistencia en MongoDB

### Fase 7: Frontend (Estación)

21. ✅ Crear página para gestionar surtidores (CRUD)
22. ✅ Mostrar surtidores conectados en tiempo real
23. ✅ Vista de transacciones por surtidor

---

## 📝 Comandos Útiles

### Registrar un surtidor antes de levantarlo

```bash
curl -X POST http://localhost:8001/api/surtidores \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Surtidor Norte 1",
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "combustible_actual": "95",
    "capacidad_maxima": 100.0
  }'
```

### Levantar estación con surtidores

```bash
cd Estacion
docker-compose up --build
```

### Ver logs de un surtidor específico

```bash
docker logs -f surtidor1-backend
```

### Probar conexión TCP manualmente

```bash
# Desde dentro del contenedor del surtidor
docker exec -it surtidor1-backend bash
nc estacion-backend 6000
# Enviar JSON:
{"tipo":"registro","id_surtidor":1,"nombre":"Test","combustibles_soportados":["95"],"version":"1.0"}
```

---

## 🎯 Resultado Final

Con esta implementación tendrás:

✅ **Surtidores como contenedores independientes** con su propio FastAPI y frontend
✅ **Comunicación TCP pura** (no WebSocket) entre surtidores y estación
✅ **CRUD completo de surtidores** desde la API de la estación
✅ **Actualización automática de precios** propagada desde Empresa → Estación → Surtidores
✅ **Transacciones guardadas en la estación** cuando los surtidores completan despachos
✅ **Reconexión automática** si se pierde la conexión
✅ **Escalable** - fácil agregar nuevos surtidores al docker-compose

---

## 📚 Próximos Pasos (Opcionales)

- Implementar autenticación/autorización
- Agregar WebSocket para notificaciones en tiempo real al frontend
- Implementar métricas y monitoreo (Prometheus/Grafana)
- Agregar logs estructurados (Logstash)
- Implementar rate limiting
- Agregar validaciones de negocio más robustas
- Crear scripts de inicialización de datos

---

**¡Listo para implementar! 🚀**
