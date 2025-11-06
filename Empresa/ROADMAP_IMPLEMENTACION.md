# 🗺️ Roadmap de Implementación - Sistema Empresa Bencinera

## 📋 Objetivo General
Implementar un sistema centralizado de gestión de estaciones de servicio con MongoDB, que permita:
- Almacenar información de estaciones (ID, nombre, IP, precios actuales e histórico)
- Actualizar precios desde el frontend
- Distribuir automáticamente los precios actualizados a todas las estaciones
- Gestionar estaciones mediante un CRUD completo

---

## 🎯 Estructura de Datos

### Modelo de Estación en MongoDB
```javascript
{
  _id: ObjectId,
  id_estacion: Integer,          // ID único de la estación
  nombre: String,                 // Nombre de la estación
  ip: String,                     // Dirección IP de la estación
  puerto: Integer,                // Puerto de conexión
  estado: String,                 // "Activa" | "Inactiva" | "Desconectada"
  precios_actuales: {
    precio_93: Integer,
    precio_95: Integer,
    precio_97: Integer,
    precio_diesel: Integer
  },
  historico_precios: [
    {
      timestamp: Date,
      precios: {
        precio_93: Integer,
        precio_95: Integer,
        precio_97: Integer,
        precio_diesel: Integer
      }
    }
  ],
  fecha_creacion: Date,
  fecha_actualizacion: Date
}
```

---

## 🚀 Plan de Implementación

### **FASE 1: Configuración de la Base de Datos MongoDB**

#### Task 1.1: Instalar dependencias de MongoDB
**Agente sugerido:** Agente de configuración de entorno

**Instrucciones:**
```
Agrega las siguientes dependencias al archivo requirements.txt del backend de Empresa:
- pymongo
- motor (para operaciones async con MongoDB)
- python-dotenv (para variables de entorno)

Instala las dependencias con: pip install -r requirements.txt
```

**Archivo a modificar:** `Empresa/backend/requirements.txt`

**Dependencias a agregar:**
```
pymongo==4.6.1
motor==3.3.2
python-dotenv==1.0.0
```

#### Task 1.2: Configurar conexión a MongoDB
**Agente sugerido:** Agente de configuración de base de datos

**Instrucciones:**
```
Crea un archivo .env en Empresa/backend/ con la siguiente configuración:
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=bencineras_db

Crea un archivo database.py en Empresa/backend/ que establezca la conexión con MongoDB usando Motor (async).
Debe exportar:
- db: instancia de la base de datos
- estaciones_collection: colección de estaciones
```

**Archivos a crear:**
- `Empresa/backend/.env`
- `Empresa/backend/database.py`

**Código sugerido para database.py:**
```python
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "bencineras_db")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
estaciones_collection = db["estaciones"]
```

---

### **FASE 2: Modelos y Esquemas de Datos**

#### Task 2.1: Crear modelos Pydantic
**Agente sugerido:** Agente de modelado de datos

**Instrucciones:**
```
Crea un archivo models.py en Empresa/backend/ con los siguientes modelos Pydantic:

1. PreciosModel: para el objeto de precios
2. HistoricoPreciosModel: para el historial con timestamp
3. EstacionModel: modelo completo de estación
4. EstacionCreate: modelo para crear una estación (sin historial)
5. EstacionUpdate: modelo para actualizar una estación
6. PreciosUpdate: modelo específico para actualizar solo precios
```

**Archivo a crear:** `Empresa/backend/models.py`

**Estructura sugerida:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PreciosModel(BaseModel):
    precio_93: int = Field(..., ge=0)
    precio_95: int = Field(..., ge=0)
    precio_97: int = Field(..., ge=0)
    precio_diesel: int = Field(..., ge=0)

class HistoricoPreciosModel(BaseModel):
    timestamp: datetime
    precios: PreciosModel

class EstacionModel(BaseModel):
    id_estacion: int
    nombre: str
    ip: str
    puerto: int = 5000
    estado: str = "Activa"
    precios_actuales: PreciosModel
    historico_precios: List[HistoricoPreciosModel] = []
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)

class EstacionCreate(BaseModel):
    nombre: str
    ip: str
    puerto: int = 5000
    precios_actuales: PreciosModel

class EstacionUpdate(BaseModel):
    nombre: Optional[str] = None
    ip: Optional[str] = None
    puerto: Optional[int] = None
    estado: Optional[str] = None

class PreciosUpdate(BaseModel):
    precios: PreciosModel
```

---

### **FASE 3: Servicios de Base de Datos (CRUD)**

#### Task 3.1: Implementar servicio CRUD para estaciones
**Agente sugerido:** Agente de lógica de negocio / Backend

**Instrucciones:**
```
Crea un archivo estaciones_service.py en Empresa/backend/ que contenga las siguientes funciones async:

1. crear_estacion(estacion: EstacionCreate) -> dict
   - Genera un ID único
   - Inserta la estación en MongoDB
   - Retorna la estación creada

2. obtener_estaciones() -> List[dict]
   - Retorna todas las estaciones

3. obtener_estacion_por_id(id_estacion: int) -> dict
   - Retorna una estación específica

4. actualizar_estacion(id_estacion: int, datos: EstacionUpdate) -> dict
   - Actualiza datos generales de la estación

5. actualizar_precios(id_estacion: int, precios: PreciosUpdate) -> dict
   - Actualiza precios actuales
   - Agrega entrada al historial con timestamp
   - Retorna la estación actualizada

6. eliminar_estacion(id_estacion: int) -> bool
   - Elimina la estación

7. obtener_historico_precios(id_estacion: int) -> List[dict]
   - Retorna el historial de precios de una estación
```

**Archivo a crear:** `Empresa/backend/estaciones_service.py`

---

### **FASE 4: Endpoints de API REST**

#### Task 4.1: Crear endpoints para el CRUD
**Agente sugerido:** Agente de desarrollo de API

**Instrucciones:**
```
Modifica el archivo main.py en Empresa/backend/ para agregar los siguientes endpoints:

GET    /api/estaciones              - Obtener todas las estaciones
GET    /api/estaciones/{id}          - Obtener una estación
POST   /api/estaciones               - Crear nueva estación
PUT    /api/estaciones/{id}          - Actualizar estación
DELETE /api/estaciones/{id}          - Eliminar estación
PUT    /api/estaciones/{id}/precios  - Actualizar precios (y guardar en historial)
GET    /api/estaciones/{id}/historico - Obtener historial de precios

Todos deben ser async y usar los servicios de estaciones_service.py
```

**Archivo a modificar:** `Empresa/backend/main.py`

**Estructura sugerida:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from models import EstacionCreate, EstacionUpdate, PreciosUpdate
from estaciones_service import (
    crear_estacion, obtener_estaciones, obtener_estacion_por_id,
    actualizar_estacion, actualizar_precios, eliminar_estacion,
    obtener_historico_precios
)
from tcp_server import iniciar_tcp_servidor

app = FastAPI(title="Backend Empresa Bencinera", version="2.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def iniciar_componentes():
    asyncio.create_task(iniciar_tcp_servidor())
    print("🚀 Servidor TCP iniciado junto con FastAPI")

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend Empresa funcionando"}

# Aquí agregar todos los endpoints del CRUD
```

---

### **FASE 5: Sistema de Distribución de Precios**

#### Task 5.1: Implementar notificación a estaciones
**Agente sugerido:** Agente de comunicación/networking

**Instrucciones:**
```
Modifica tcp_server.py para:
1. Mantener un registro de estaciones conectadas con su IP
2. Crear una función enviar_precios_a_estacion(ip: str, puerto: int, precios: dict)
3. Crear una función broadcast_precios(id_estacion: int, precios: dict) que envíe los precios a la estación específica

Integra esta función con el endpoint PUT /api/estaciones/{id}/precios para que automáticamente envíe los nuevos precios a la estación cuando se actualicen desde el frontend.
```

**Archivo a modificar:** `Empresa/backend/tcp_server.py`

**Funcionalidad a agregar:**
```python
import socket
import json

# Diccionario global de estaciones conectadas
estaciones_conectadas = {}

async def enviar_precios_a_estacion(ip: str, puerto: int, precios: dict):
    """Envía los precios actualizados a una estación específica"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, puerto))
        
        mensaje = {
            "tipo": "actualizacion_precios",
            "timestamp": datetime.now().isoformat(),
            "precios": precios
        }
        
        s.sendall((json.dumps(mensaje) + "\n").encode())
        s.close()
        print(f"✅ Precios enviados a {ip}:{puerto}")
        return True
    except Exception as e:
        print(f"❌ Error enviando precios a {ip}:{puerto}: {e}")
        return False
```

#### Task 5.2: Integrar distribución con actualización de precios
**Agente sugerido:** Agente de integración

**Instrucciones:**
```
En estaciones_service.py, modifica la función actualizar_precios para que:
1. Actualice los precios en la base de datos
2. Llame a enviar_precios_a_estacion con la IP y puerto de la estación
3. Retorne el resultado indicando si se envió correctamente

Asegúrate de importar la función desde tcp_server.py
```

---

### **FASE 6: Frontend - Interfaz de Gestión de Estaciones**

#### Task 6.1: Crear página de gestión de estaciones
**Agente sugerido:** Agente de desarrollo frontend

**Instrucciones:**
```
Crea una nueva página en Empresa/frontend/src/app/estaciones/page.js que incluya:

1. Tabla/Lista de todas las estaciones con:
   - ID, Nombre, IP, Puerto, Estado
   - Precios actuales
   - Botones: Editar, Eliminar, Ver Historial

2. Botón "Agregar Nueva Estación" que abra un modal/formulario

3. Formulario de creación/edición con campos:
   - Nombre
   - IP
   - Puerto
   - Precios iniciales (93, 95, 97, diesel)

4. Conectar con los endpoints del backend usando fetch o axios
```

**Archivo a crear:** `Empresa/frontend/src/app/estaciones/page.js`

#### Task 6.2: Crear componente de actualización de precios
**Agente sugerido:** Agente de desarrollo frontend

**Instrucciones:**
```
Crea un componente ActualizarPrecios en Empresa/frontend/src/components/ActualizarPrecios.jsx que:

1. Reciba el ID de la estación y los precios actuales como props
2. Muestre un formulario con inputs para cada tipo de combustible
3. Al guardar, haga PUT a /api/estaciones/{id}/precios
4. Muestre mensaje de éxito/error
5. Actualice la lista de estaciones

El componente puede ser un Dialog/Modal similar al que ya existe en page.js
```

**Archivo a crear:** `Empresa/frontend/src/components/ActualizarPrecios.jsx`

#### Task 6.3: Crear página de visualización de historial
**Agente sugerido:** Agente de visualización de datos

**Instrucciones:**
```
Crea una página Empresa/frontend/src/app/estaciones/[id]/historico/page.js que:

1. Obtenga el ID de la estación de los parámetros de la URL
2. Haga GET a /api/estaciones/{id}/historico
3. Muestre una tabla o timeline con:
   - Fecha/hora de cada cambio
   - Precios en ese momento
4. Opcionalmente, agregar un gráfico de evolución de precios (usar recharts o similar)
```

**Archivo a crear:** `Empresa/frontend/src/app/estaciones/[id]/historico/page.js`

#### Task 6.4: Actualizar navegación
**Agente sugerido:** Agente de UI/UX

**Instrucciones:**
```
Modifica el componente Navbar.jsx para agregar un enlace a la nueva página de gestión de estaciones:
- Agregar enlace "Gestión de Estaciones" que apunte a /estaciones
- Mantener la página principal (dashboard en tiempo real)
```

**Archivo a modificar:** `Empresa/frontend/src/components/Navbar.jsx`

---

### **FASE 7: Adaptación del Backend de Estación**

#### Task 7.1: Modificar receptor de precios en Estación
**Agente sugerido:** Agente de integración

**Instrucciones:**
```
Modifica tcp_server.py en Estacion/backend/ para:

1. Detectar mensajes con tipo "actualizacion_precios"
2. Extraer los nuevos precios del mensaje
3. Actualizar los precios en el estado local de la estación
4. Propagar los nuevos precios al frontend de la estación via WebSocket

Asegúrate de que surtidor_simulado.py use estos precios actualizados en lugar de valores hardcodeados.
```

**Archivos a modificar:**
- `Estacion/backend/tcp_server.py`
- `Estacion/backend/surtidor_simulado.py`

**Modificación sugerida en surtidor_simulado.py:**
```python
# En lugar de precios fijos, obtener precios del servidor
# Agregar un listener para actualizaciones de precios
# Actualizar el diccionario surtidor con los nuevos precios recibidos
```

---

### **FASE 8: Testing y Validación**

#### Task 8.1: Pruebas de CRUD
**Agente sugerido:** Agente de testing

**Instrucciones:**
```
Realiza las siguientes pruebas:

1. Crear una estación desde el frontend
2. Verificar que se guarde en MongoDB
3. Actualizar datos generales de la estación
4. Actualizar precios y verificar:
   - Se guarden en precios_actuales
   - Se agregue entrada al historial
   - Se envíen a la estación correspondiente
5. Ver historial de precios
6. Eliminar estación

Documenta cualquier error encontrado.
```

#### Task 8.2: Pruebas de comunicación
**Agente sugerido:** Agente de testing de integración

**Instrucciones:**
```
Prueba el flujo completo:

1. Levanta MongoDB
2. Inicia backend de Empresa
3. Inicia frontend de Empresa
4. Inicia backend y frontend de Estación
5. Crea una estación en el sistema Empresa con la IP de la Estación
6. Actualiza precios desde el frontend de Empresa
7. Verifica que el frontend de Estación muestre los nuevos precios

Documenta el tiempo de propagación y cualquier problema.
```

---

## 📦 Dependencias Adicionales a Instalar

### Backend (Python)
```bash
cd Empresa/backend
pip install pymongo motor python-dotenv
```

### Frontend (Node.js)
```bash
cd Empresa/frontend
npm install axios  # Si no está instalado
```

---

## 🗄️ Configuración de MongoDB

### Opción 1: MongoDB Local
```bash
# Instalar MongoDB Community Edition
# Windows: https://www.mongodb.com/try/download/community
# Iniciar servicio:
mongod --dbpath C:\data\db
```

### Opción 2: MongoDB Atlas (Cloud)
```
1. Crear cuenta en https://www.mongodb.com/cloud/atlas
2. Crear cluster gratuito
3. Obtener connection string
4. Actualizar .env con la URL de conexión
```

### Opción 3: Docker
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

## 🔄 Orden de Ejecución para Agentes

### Secuencia Recomendada:
1. **Fase 1** → Configuración completa antes de continuar
2. **Fase 2** → Modelos definidos
3. **Fase 3** → Servicios implementados
4. **Fase 4** → API REST funcional → **PUNTO DE PRUEBA 1**
5. **Fase 5** → Sistema de distribución
6. **Fase 6** → Frontend completo → **PUNTO DE PRUEBA 2**
7. **Fase 7** → Integración con Estación
8. **Fase 8** → Testing final → **PUNTO DE PRUEBA 3**

### Puntos de Validación:
- **Punto 1:** Probar endpoints con Postman/Thunder Client
- **Punto 2:** Probar CRUD desde frontend
- **Punto 3:** Probar flujo completo Empresa ↔ Estación

---

## 📝 Notas Importantes

### Estructura de Mensajes entre Empresa y Estación:
```json
{
  "tipo": "actualizacion_precios",
  "timestamp": "2025-11-06T10:30:00",
  "precios": {
    "precio_93": 1290,
    "precio_95": 1350,
    "precio_97": 1400,
    "precio_diesel": 1120
  }
}
```

### Variables de Entorno (.env):
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=bencineras_db
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Puertos Utilizados:
- MongoDB: `27017`
- Backend Empresa (FastAPI): `8000`
- Frontend Empresa (Next.js): `3000`
- TCP Server Empresa: `5000` (comunicación con estaciones)
- WebSocket Bridge Empresa: `4000`
- Backend Estación (FastAPI): `8001`
- Frontend Estación (Next.js): `3001`

---

## 🎯 Resultado Esperado

Al finalizar la implementación, deberás tener:

1. ✅ Sistema de gestión de estaciones con CRUD completo
2. ✅ Base de datos MongoDB con información de estaciones
3. ✅ Historial de precios por estación con timestamps
4. ✅ Sistema de distribución automática de precios a estaciones
5. ✅ Interfaz frontend para gestionar estaciones y precios
6. ✅ Visualización de historial de precios
7. ✅ Comunicación bidireccional Empresa ↔ Estaciones
8. ✅ Dashboard en tiempo real actualizado con precios centralizados

---

## 🚨 Consideraciones de Seguridad

1. **Autenticación:** Considerar agregar JWT para proteger endpoints
2. **Validación:** Validar IPs y puertos antes de conectar
3. **Rate Limiting:** Limitar actualizaciones de precios para evitar spam
4. **Logs:** Implementar logging de todas las operaciones críticas
5. **Backup:** Configurar respaldo automático de MongoDB

---

## 📚 Recursos Útiles

- [Motor Documentation](https://motor.readthedocs.io/)
- [FastAPI + MongoDB](https://www.mongodb.com/compatibility/mongodb-and-fastapi)
- [Pydantic Models](https://docs.pydantic.dev/)
- [Next.js Dynamic Routes](https://nextjs.org/docs/routing/dynamic-routes)

---

**Versión:** 1.0  
**Fecha:** Noviembre 2025  
**Proyecto:** Sistema Distribuido Bencineras
