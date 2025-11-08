# Análisis Técnico: Integración de Surtidores en Estaciones

## 📋 Resumen Ejecutivo

Este documento analiza la viabilidad y propone la arquitectura para integrar los surtidores dentro de las estaciones de servicio, utilizando **comunicación por sockets TCP** (no WebSockets), similar al modelo Empresa → Estación.

### Objetivos
1. ✅ **CRUD de Surtidores**: Gestionar surtidores desde la estación
2. ✅ **Actualización de Precios**: Propagar precios solo cuando los surtidores estén disponibles
3. ✅ **Registro de Transacciones**: Guardar transacciones en la base de datos de la estación
4. ✅ **Comunicación TCP**: Usar sockets TCP puros (no WebSockets)

---

## 🏗️ Arquitectura Actual

### Sistema Empresa → Estación (Modelo a Replicar)

```
┌─────────────────┐                         ┌──────────────────┐
│    EMPRESA      │                         │    ESTACIÓN      │
│                 │                         │                  │
│  - MongoDB      │    Socket TCP 5001      │  - MongoDB       │
│  - FastAPI      │  ◄──────────────────►  │  - FastAPI       │
│  - TCP Client   │                         │  - TCP Server    │
│                 │   Actualiz. Precios     │                  │
│  Actualiza      │  ──────────────────►   │  Recibe y        │
│  precios en     │                         │  almacena        │
│  estaciones     │                         │  precios         │
└─────────────────┘                         └──────────────────┘
```

**Características clave:**
- ✅ Comunicación **bidireccional** con TCP
- ✅ Mensajes JSON delimitados por `\n`
- ✅ Reconexión automática si se pierde la conexión
- ✅ Propagación de precios desde Empresa a Estación
- ✅ Estado persistente en MongoDB

---

## 🎯 Arquitectura Propuesta: Estación → Surtidor

### Diagrama de Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│                          EMPRESA                                  │
│  - Gestiona múltiples estaciones                                 │
│  - Actualiza precios globalmente                                 │
│  - MongoDB (puerto 27017)                                        │
└────────────────┬─────────────────────────────────────────────────┘
                 │ TCP Socket (5001)
                 │ Actualización de precios
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                         ESTACIÓN                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Backend FastAPI (8001)                                  │    │
│  │  - API REST para el frontend                            │    │
│  │  - CRUD de Surtidores                                   │    │
│  │  - Gestión de transacciones                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ TCP Server Surtidores (puerto 6000)                     │    │
│  │  - Escucha conexiones de surtidores                     │    │
│  │  - Recibe estados de surtidores                         │    │
│  │  - Envía precios actualizados                           │    │
│  │  - Maneja reconexiones                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ MongoDB (puerto 27018)                                  │    │
│  │  Colecciones:                                           │    │
│  │   - transacciones                                       │    │
│  │   - surtidores                                          │    │
│  │   - estado_surtidores (cache en tiempo real)            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ WebSocket Bridge (4001)                                 │    │
│  │  - Conecta frontend con backend TCP                     │    │
│  │  - Notificaciones en tiempo real                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────┬───────────────┬───────────────┬────────────────────┘
             │               │               │
             │ TCP 6000      │ TCP 6000      │ TCP 6000
             ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  SURTIDOR 1  │ │  SURTIDOR 2  │ │  SURTIDOR N  │
     │              │ │              │ │              │
     │ - Backend    │ │ - Backend    │ │ - Backend    │
     │   FastAPI    │ │   FastAPI    │ │   FastAPI    │
     │ - TCP Client │ │ - TCP Client │ │ - TCP Client │
     │ - Frontend   │ │ - Frontend   │ │ - Frontend   │
     │   (opcional) │ │   (opcional) │ │   (opcional) │
     └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🔍 Análisis de Viabilidad

### ✅ **VIABLE - Socket TCP en lugar de WebSocket**

**Razones:**
1. ✅ **Consistencia arquitectónica**: Ya usamos TCP para Empresa→Estación
2. ✅ **Menor overhead**: TCP puro es más eficiente que WebSocket para este caso
3. ✅ **Bidireccional**: TCP soporta comunicación bidireccional
4. ✅ **Reconexión**: Podemos implementar lógica de reconexión automática
5. ✅ **Simplicidad**: Mensajes JSON delimitados por `\n` (misma estrategia actual)

**Diferencias con WebSocket:**
- No hay handshake HTTP inicial
- No hay framing de mensajes WebSocket
- No hay soporte de navegador directo (los surtidores son backends, no browsers)
- Más control sobre el protocolo

---

## 📊 Modelos de Datos

### 1. Surtidor (Colección en MongoDB)

```python
{
    "_id": ObjectId("..."),
    "id_surtidor": 1,  # ID único autoincrementado
    "nombre": "Surtidor Norte 1",
    "estado": "disponible",  # disponible, ocupado, fuera_servicio, desconectado
    "ip": "192.168.1.101",
    "puerto": 8000,
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "combustible_actual": "95",  # Tipo de combustible configurado
    "fecha_creacion": "2024-01-15T10:00:00",
    "fecha_actualizacion": "2024-01-15T14:30:00",
    "ultima_conexion": "2024-01-15T14:30:00",
    "configuracion": {
        "capacidad_maxima_litros": 100.0,
        "velocidad_despacho": 1.0  # litros por segundo
    }
}
```

### 2. Estado del Surtidor (Cache en Tiempo Real)

```python
{
    "_id": ObjectId("..."),
    "id_surtidor": 1,
    "estado_conexion": "conectado",  # conectado, desconectado
    "estado_operacion": "disponible",  # disponible, despachando, pausado
    "litros_actuales": 0.0,
    "monto_actual": 0,
    "tipo_combustible": "95",
    "precio_por_litro": 1350,
    "cliente_id": null,  # null o ID de cliente si está ocupado
    "timestamp": "2024-01-15T14:30:00"
}
```

### 3. Transacción

```python
{
    "_id": ObjectId("..."),
    "id_surtidor": 1,
    "nombre_surtidor": "Surtidor Norte 1",
    "tipo_combustible": "95",
    "litros": 30.5,
    "precio_por_litro": 1350,
    "monto_total": 41175,
    "metodo_pago": "tarjeta",  # efectivo, tarjeta, transferencia
    "fecha_inicio": "2024-01-15T14:25:00",
    "fecha_fin": "2024-01-15T14:30:00",
    "estado": "completada",  # iniciada, completada, cancelada, error
    "operador": "Juan Pérez",  # opcional
    "detalles": {
        "duracion_segundos": 305,
        "velocidad_promedio": 0.1  # litros por segundo
    }
}
```

---

## 📡 Protocolo de Comunicación TCP

### Formato de Mensajes

Todos los mensajes son **JSON delimitados por `\n`** (newline):

```json
{"tipo": "mensaje_tipo", "datos": {...}}\n
```

### 1. Mensajes Surtidor → Estación

#### a) Registro Inicial (al conectar)
```json
{
    "tipo": "registro",
    "id_surtidor": 1,
    "nombre": "Surtidor Norte 1",
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "version": "1.0"
}\n
```

#### b) Actualización de Estado (cada 2-5 segundos o al cambiar)
```json
{
    "tipo": "estado",
    "id_surtidor": 1,
    "estado_operacion": "despachando",
    "litros_actuales": 15.5,
    "monto_actual": 20925,
    "tipo_combustible": "95",
    "timestamp": "2024-01-15T14:30:00"
}\n
```

#### c) Transacción Completada
```json
{
    "tipo": "transaccion_completada",
    "id_surtidor": 1,
    "tipo_combustible": "95",
    "litros": 30.5,
    "precio_por_litro": 1350,
    "monto_total": 41175,
    "metodo_pago": "tarjeta",
    "fecha_inicio": "2024-01-15T14:25:00",
    "fecha_fin": "2024-01-15T14:30:00"
}\n
```

#### d) Error/Alerta
```json
{
    "tipo": "error",
    "id_surtidor": 1,
    "codigo": "ERROR_DESPACHO",
    "mensaje": "Error en el sensor de flujo",
    "timestamp": "2024-01-15T14:30:00"
}\n
```

#### e) Heartbeat (cada 30 segundos)
```json
{
    "tipo": "heartbeat",
    "id_surtidor": 1,
    "timestamp": "2024-01-15T14:30:00"
}\n
```

### 2. Mensajes Estación → Surtidor

#### a) Confirmación de Registro
```json
{
    "tipo": "registro_confirmado",
    "id_surtidor": 1,
    "mensaje": "Surtidor registrado exitosamente",
    "precios": {
        "precio_93": 1290,
        "precio_95": 1350,
        "precio_97": 1400,
        "precio_diesel": 1120
    }
}\n
```

#### b) Actualización de Precios
```json
{
    "tipo": "actualizacion_precios",
    "precios": {
        "precio_93": 1290,
        "precio_95": 1350,
        "precio_97": 1400,
        "precio_diesel": 1120
    },
    "timestamp": "2024-01-15T14:30:00"
}\n
```

#### c) Comando de Control
```json
{
    "tipo": "comando",
    "comando": "pausar|reanudar|detener_emergencia",
    "razon": "Mantenimiento programado"
}\n
```

#### d) Solicitud de Estado
```json
{
    "tipo": "solicitud_estado",
    "timestamp": "2024-01-15T14:30:00"
}\n
```

---

## 🛠️ Endpoints API REST (Estación)

### CRUD de Surtidores

#### GET `/api/surtidores`
Lista todos los surtidores registrados en la estación.

**Response:**
```json
[
    {
        "id_surtidor": 1,
        "nombre": "Surtidor Norte 1",
        "estado": "disponible",
        "estado_conexion": "conectado",
        "combustible_actual": "95",
        "ultima_conexion": "2024-01-15T14:30:00"
    }
]
```

#### GET `/api/surtidores/{id_surtidor}`
Obtiene detalles de un surtidor específico.

**Response:**
```json
{
    "id_surtidor": 1,
    "nombre": "Surtidor Norte 1",
    "estado": "disponible",
    "ip": "192.168.1.101",
    "puerto": 8000,
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "combustible_actual": "95",
    "estadisticas": {
        "total_transacciones": 120,
        "litros_totales": 3650.5,
        "ingresos_totales": 4927175
    }
}
```

#### POST `/api/surtidores`
Registra un nuevo surtidor (pre-configuración antes de conectar).

**Request:**
```json
{
    "nombre": "Surtidor Norte 1",
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "combustible_actual": "95"
}
```

#### PUT `/api/surtidores/{id_surtidor}`
Actualiza configuración del surtidor.

**Request:**
```json
{
    "nombre": "Surtidor Norte 1 - Actualizado",
    "combustible_actual": "97"
}
```

#### DELETE `/api/surtidores/{id_surtidor}`
Elimina un surtidor del sistema.

### Estado en Tiempo Real

#### GET `/api/surtidores/{id_surtidor}/estado`
Obtiene el estado actual del surtidor.

**Response:**
```json
{
    "estado_conexion": "conectado",
    "estado_operacion": "despachando",
    "litros_actuales": 15.5,
    "monto_actual": 20925,
    "tipo_combustible": "95",
    "precio_por_litro": 1350
}
```

#### GET `/api/surtidores/estado/conectados`
Lista todos los surtidores conectados actualmente.

### Transacciones

#### GET `/api/surtidores/{id_surtidor}/transacciones`
Lista transacciones de un surtidor específico.

**Query params:**
- `limit` (default: 50)
- `skip` (default: 0)
- `fecha_inicio`
- `fecha_fin`

#### GET `/api/transacciones`
Lista todas las transacciones de la estación (ya existe en el código actual).

---

## 🔒 Manejo de Conexiones y Errores

### Reconexión Automática (Surtidor)

```python
async def conectar_a_estacion():
    """Cliente TCP con reconexión automática"""
    max_intentos = 5
    delay_base = 2  # segundos
    
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                ESTACION_HOST, 
                ESTACION_PORT
            )
            print(f"✅ Conectado a estación")
            
            # Enviar registro
            await enviar_registro(writer)
            
            # Mantener conexión y procesar mensajes
            await procesar_mensajes(reader, writer)
            
        except ConnectionRefusedError:
            print(f"⚠️ Estación no disponible. Reintentando...")
            await asyncio.sleep(delay_base)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(delay_base)
```

### Detección de Desconexión (Estación)

```python
async def manejar_surtidor(reader, writer):
    """Servidor TCP que maneja conexiones de surtidores"""
    addr = writer.get_extra_info('peername')
    
    try:
        # Recibir registro
        registro = await asyncio.wait_for(
            reader.readline(), 
            timeout=10.0
        )
        surtidor_data = json.loads(registro.decode())
        id_surtidor = surtidor_data["id_surtidor"]
        
        # Registrar conexión
        await registrar_conexion(id_surtidor, addr)
        
        # Enviar precios actuales
        await enviar_precios_actuales(writer)
        
        # Loop de mensajes
        last_heartbeat = time.time()
        
        while True:
            data = await asyncio.wait_for(
                reader.readline(), 
                timeout=60.0  # timeout de 60 segundos
            )
            
            if not data:
                break
                
            # Procesar mensaje
            mensaje = json.loads(data.decode())
            await procesar_mensaje_surtidor(id_surtidor, mensaje)
            last_heartbeat = time.time()
            
    except asyncio.TimeoutError:
        print(f"⚠️ Timeout: Surtidor {id_surtidor} sin heartbeat")
        
    except Exception as e:
        print(f"❌ Error con surtidor {id_surtidor}: {e}")
        
    finally:
        # Marcar como desconectado
        await marcar_desconectado(id_surtidor)
        writer.close()
        await writer.wait_closed()
```

### Estados de Conexión

```python
Estados posibles:
- "conectado": Surtidor activo y enviando heartbeats
- "desconectado": Sin conexión TCP
- "timeout": Sin heartbeat por más de 60 segundos
- "error": Error en la comunicación
```

---

## 🔄 Flujo de Actualización de Precios

```
EMPRESA actualiza precio
        │
        ├─► Envía mensaje TCP a ESTACIÓN (puerto 5001)
        │
ESTACIÓN recibe actualización
        │
        ├─► Actualiza precios_actuales en memoria
        ├─► Guarda en MongoDB (opcional: historial)
        │
        ├─► Propaga a todos los SURTIDORES conectados
        │   │
        │   ├─► Surtidor 1 (conectado) ✅ Recibe precios
        │   ├─► Surtidor 2 (conectado) ✅ Recibe precios
        │   └─► Surtidor 3 (desconectado) ❌ No recibe
        │
        └─► Cuando Surtidor 3 reconecta:
                └─► Recibe precios actuales en el registro_confirmado
```

**Garantías:**
- ✅ Surtidores conectados reciben precios en tiempo real
- ✅ Surtidores desconectados reciben precios al reconectar
- ✅ Sin pérdida de actualizaciones

---

## 📈 Ventajas de esta Arquitectura

### 1. **Consistencia con Sistema Actual**
- Usa el mismo patrón TCP que Empresa→Estación
- Reutiliza lógica de reconexión y manejo de mensajes
- Desarrolladores ya familiarizados con el patrón

### 2. **Escalabilidad**
- Soporta N surtidores por estación
- Bajo overhead de red (TCP puro)
- Estado en memoria + persistencia en MongoDB

### 3. **Resiliencia**
- Reconexión automática
- Heartbeats para detectar desconexiones
- Estado persistente sobrevive reinicios

### 4. **Simplicidad**
- No requiere WebSocket (menos dependencias)
- Mensajes JSON fáciles de debuggear
- Lógica clara de cliente/servidor

### 5. **Compatibilidad**
- Surtidores pueden correr en cualquier lenguaje
- No dependen de navegadores
- Fácil testing con herramientas como `netcat` o `telnet`

---

## ⚠️ Consideraciones y Limitaciones

### 1. **Sin Frontend Directo en Surtidor**
- Los surtidores no tienen navegador conectado directo a la estación
- Frontend del surtidor se conecta a su propio backend FastAPI
- El backend del surtidor se conecta por TCP a la estación

### 2. **Seguridad**
- TCP sin encriptación (agregar TLS si es necesario)
- Autenticación básica en el registro
- Considerar VPN para despliegues en producción

### 3. **Sincronización**
- Estado distribuido entre surtidores y estación
- Posibles race conditions en transacciones simultáneas
- Implementar locks o validaciones adecuadas

### 4. **Monitoreo**
- Logs centralizados en la estación
- Métricas de conexión y performance
- Alertas para surtidores desconectados

---

## 🎯 Conclusión

✅ **COMPLETAMENTE VIABLE** implementar surtidores con comunicación TCP pura.

**Próximos pasos:**
1. Implementar modelos de datos en `models.py`
2. Crear `surtidores_service.py` con lógica CRUD
3. Implementar `tcp_server_surtidores.py` para manejar conexiones
4. Actualizar backend del surtidor para usar TCP client
5. Crear endpoints REST para el frontend
6. Testing end-to-end con múltiples surtidores

**Documento de implementación detallado en:** `DESARROLLO_SURTIDORES.md`
