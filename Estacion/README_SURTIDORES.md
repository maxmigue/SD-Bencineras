# 🏪 Estación con Surtidores - Guía de Uso

## 📋 Arquitectura

```
Estación (docker-compose.yml)
├── MongoDB (puerto 27018)
├── Backend Estación (puerto 8001)
│   ├── TCP Empresa (puerto 5001)
│   ├── TCP Surtidores (puerto 6001)
│   └── UDP Surtidores (puerto 6002)
├── Frontend Estación (puerto 3001)
└── Surtidores (en la misma red)
    ├── Surtidor 1: Backend 8002, Frontend 3002
    ├── Surtidor 2: Backend 8003, Frontend 3003
    └── Surtidor 3: Backend 8004, Frontend 3004
```

## 🚀 Inicio Rápido

### 1️⃣ Levantar Todo el Sistema

```bash
# En directorio Estacion/
docker-compose up -d
```

**¡Eso es todo!** Los surtidores se auto-registran al conectarse por primera vez.

Esperar a que los servicios estén listos (30-60 segundos):
```bash
docker-compose logs -f
```

### 2️⃣ Verificar Auto-Registro

Los surtidores se registran automáticamente cuando se conectan por TCP:
- Surtidor 1: ID=1, Nombre="Surtidor Norte 1"
- Surtidor 2: ID=2, Nombre="Surtidor Sur 1"  
- Surtidor 3: ID=3, Nombre="Surtidor Este 1"

```bash
# Ver todos los surtidores registrados
curl http://localhost:8001/api/surtidores | jq
```

### 3️⃣ (Opcional) Registro Manual

Si prefieres crear surtidores antes de levantarlos:

```bash
# Levantar solo la infraestructura base
docker-compose up -d mongodb backend frontend

# Registrar manualmente
curl -X POST http://localhost:8001/api/surtidores \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Surtidor Personalizado",
    "combustibles_soportados": ["93", "95", "97", "diesel"],
    "combustible_actual": "95",
    "capacidad_maxima": 100.0
  }'

# Luego levantar surtidores
docker-compose up -d surtidor1-backend surtidor1-frontend
```

### 4️⃣ Comandos Útiles

```bash
# Levantar todos los surtidores
docker-compose up -d surtidor1-backend surtidor1-frontend \
                     surtidor2-backend surtidor2-frontend \
                     surtidor3-backend surtidor3-frontend
```

O de forma individual:
```bash
# Solo Surtidor 1
docker-compose up -d surtidor1-backend surtidor1-frontend

# Solo Surtidor 2
docker-compose up -d surtidor2-backend surtidor2-frontend

# Solo Surtidor 3
docker-compose up -d surtidor3-backend surtidor3-frontend
```

### 4️⃣ Verificar Estado

```bash
# Ver todos los surtidores registrados
curl http://localhost:8001/api/surtidores | jq

# Ver solo surtidores conectados
curl http://localhost:8001/api/surtidores/conectados | jq

# Ver estadísticas
curl http://localhost:8001/api/surtidores/estadisticas | jq
```

## 🌐 URLs de Acceso

### Estación
- **Frontend**: http://localhost:3001
- **API**: http://localhost:8001
- **Docs API**: http://localhost:8001/docs

### Surtidores
- **Surtidor 1**: 
  - Backend: http://localhost:8002
  - Frontend: http://localhost:3002
- **Surtidor 2**: 
  - Backend: http://localhost:8003
  - Frontend: http://localhost:3003
- **Surtidor 3**: 
  - Backend: http://localhost:8004
  - Frontend: http://localhost:3004

## 🔍 Monitoreo

### Ver logs en tiempo real

```bash
# Estación
docker logs -f estacion-backend

# Surtidor 1
docker logs -f surtidor1-backend

# Todos los surtidores
docker-compose logs -f surtidor1-backend surtidor2-backend surtidor3-backend
```

### Verificar conexiones TCP

```bash
# Ver puertos abiertos
netstat -an | grep 6001  # TCP Surtidores
netstat -an | grep 6002  # UDP Surtidores
```

## 🧪 Flujo de Prueba Completo

### 1. Iniciar despacho en Surtidor 1

```bash
curl -X POST http://localhost:8002/control/iniciar-carga
```

### 2. Ver estado en tiempo real

```bash
# Estado del surtidor
curl http://localhost:8002/estado | jq

# Ver logs de la estación (recibirá estados por UDP)
docker logs -f estacion-backend
```

### 3. Detener despacho y registrar transacción

```bash
curl -X POST "http://localhost:8002/control/detener-carga?metodo_pago=tarjeta"
```

### 4. Verificar transacción guardada en la estación

```bash
# Todas las transacciones
curl http://localhost:8001/transacciones | jq

# Transacciones del Surtidor 1
curl http://localhost:8001/api/surtidores/1/transacciones | jq
```

### 5. Ver estadísticas del surtidor

```bash
curl http://localhost:8001/api/surtidores/1 | jq
```

## 🔄 Propagación de Precios

### Simular actualización desde Empresa

```bash
# La Empresa actualiza precios (puerto 5001 TCP)
echo '{"tipo":"actualizacion_precios","precios":{"precio_93":1300,"precio_95":1360,"precio_97":1410,"precio_diesel":1130},"timestamp":"2024-01-15T10:00:00"}' | nc localhost 5001
```

Esto propagará automáticamente:
1. Empresa → Estación (TCP puerto 5001)
2. Estación → Todos los Surtidores (TCP puerto 6001)

Ver en logs:
```bash
docker logs -f estacion-backend  # Ver propagación
docker logs -f surtidor1-backend # Ver recepción
```

## 🛠️ Comandos Útiles

### Reiniciar todo

```bash
docker-compose down
docker-compose up -d
```

### Agregar un nuevo surtidor (Surtidor 4)

1. Editar `docker-compose.yml`:
```yaml
surtidor4-backend:
  build:
    context: ../Surtidor/backend
  container_name: surtidor4-backend
  ports:
    - "8005:8000"
  environment:
    - ESTACION_HOST=estacion-backend
    - ESTACION_TCP_PORT=6000
    - ESTACION_UDP_PORT=6001
    - ID_SURTIDOR=4
    - NOMBRE_SURTIDOR=Surtidor Oeste 1
  networks:
    - estacion-network
```

2. Levantar (se auto-registra al conectarse):
```bash
docker-compose up -d surtidor4-backend surtidor4-frontend
```

**Nota**: El surtidor se registrará automáticamente con ID=4 al conectarse por TCP.

### Eliminar un surtidor

```bash
# 1. Detener contenedor
docker-compose stop surtidor3-backend surtidor3-frontend

# 2. Eliminar de BD (solo si está desconectado)
curl -X DELETE http://localhost:8001/api/surtidores/3

# 3. Remover contenedor
docker-compose rm -f surtidor3-backend surtidor3-frontend
```

## 📊 Endpoints API Completos

### Surtidores
- `GET /api/surtidores` - Listar todos
- `GET /api/surtidores/conectados` - Solo conectados
- `GET /api/surtidores/estadisticas` - Estadísticas generales
- `GET /api/surtidores/{id}` - Detalles de uno
- `POST /api/surtidores` - Registrar nuevo
- `PUT /api/surtidores/{id}` - Actualizar configuración
- `DELETE /api/surtidores/{id}` - Eliminar
- `GET /api/surtidores/{id}/transacciones` - Transacciones del surtidor

### Transacciones
- `GET /transacciones` - Todas las transacciones
- `GET /transacciones?surtidor_id=1` - Filtrar por surtidor
- `GET /transacciones/{id}` - Una específica

### Estado
- `GET /estado` - Estado general de la estación
- `GET /precios` - Precios actuales

## 🐛 Troubleshooting

### Surtidor no se conecta

```bash
# Verificar que el backend de la estación esté corriendo
docker ps | grep estacion-backend

# Verificar logs del surtidor
docker logs surtidor1-backend

# Verificar red
docker network inspect estacion_estacion-network
```

### Transacciones no se guardan

```bash
# Verificar conexión MongoDB
docker exec -it estacion-backend python -c "from database import verificar_conexion; import asyncio; asyncio.run(verificar_conexion())"

# Ver colección de transacciones
docker exec -it estacion-mongodb mongosh estacion_db --eval "db.transacciones.find().pretty()"
```

### Puerto en uso

```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8002

# Cambiar puerto en docker-compose.yml
ports:
  - "8010:8000"  # Usar puerto diferente
```

## 📝 Notas

- **Auto-registro**: Los surtidores se crean automáticamente en la BD al conectarse por primera vez
- **ID del surtidor**: Se toma del `ID_SURTIDOR` en docker-compose.yml
- **UDP**: Se usa solo durante despacho (estados rápidos cada 1 segundo)
- **TCP**: Se usa para todo lo demás (registro, transacciones, comandos, heartbeat)
- **Heartbeat**: Cada 30 segundos mantiene la conexión viva
- **Timeout**: 90 segundos sin heartbeat = desconexión automática

## 🔐 Seguridad

Para producción considerar:
- TLS/SSL en conexiones TCP
- Autenticación de surtidores
- Red privada (no exponer puertos)
- Firewall rules
- Rate limiting en API
