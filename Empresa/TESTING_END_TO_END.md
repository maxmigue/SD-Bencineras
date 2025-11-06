# 🧪 Plan de Testing End-to-End - Sistema Empresa Bencineras

**Fecha de Testing:** _______________  
**Tester:** _______________  
**Versión:** 2.0

---

## 📋 Pre-requisitos

### Ambiente de Testing

- [ ] MongoDB corriendo (puerto 27017)
- [ ] Backend Empresa corriendo (puerto 8000)
- [ ] Frontend Empresa corriendo (puerto 3000)
- [ ] Backend Estación corriendo (puerto 8001)
- [ ] Frontend Estación corriendo (puerto 3001)
- [ ] WebSocket Bridge Empresa (puerto 4000)
- [ ] WebSocket Bridge Estación (puerto 4001)

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🗄️ FASE 1: Testing de Base de Datos

### 1.1 Verificar Conexión a MongoDB

- [ ] Ejecutar: `docker ps` y verificar que MongoDB está corriendo
- [ ] Acceder a MongoDB: `mongosh` o MongoDB Compass
- [ ] Verificar que existe la base de datos `bencineras_db`
- [ ] Verificar que existe la colección `estaciones`

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 1.2 Testing Manual de Colección

- [ ] Insertar un documento de prueba manualmente en MongoDB
- [ ] Verificar que el documento tiene la estructura correcta
- [ ] Eliminar el documento de prueba

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🔌 FASE 2: Testing de API REST (Backend)

### 2.1 Health Check

- [ ] **GET** `http://localhost:8000/`
  - Esperado: `{"status": "ok", "message": "...", "version": "2.0"}`
  
**Observaciones:**
```
_____________________________________________________________________________
```

### 2.2 Documentación Automática

- [ ] Acceder a `http://localhost:8000/docs` (Swagger UI)
- [ ] Verificar que todos los endpoints estén documentados
- [ ] Verificar que los modelos se muestren correctamente

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.3 CRUD - Crear Estación (POST)

- [ ] **POST** `http://localhost:8000/api/estaciones`
  ```json
  {
    "nombre": "Estación Test 1",
    "ip": "192.168.1.100",
    "puerto": 5000,
    "precios_actuales": {
      "precio_93": 1290,
      "precio_95": 1350,
      "precio_97": 1400,
      "precio_diesel": 1120
    }
  }
  ```
- [ ] Verificar respuesta con status 201
- [ ] Verificar que se generó un `id_estacion` automáticamente
- [ ] Verificar que `historico_precios` tiene una entrada inicial
- [ ] Verificar que `estado` es "Activa" por defecto

**ID generado:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.4 CRUD - Listar Estaciones (GET)

- [ ] **GET** `http://localhost:8000/api/estaciones`
- [ ] Verificar que retorna un array
- [ ] Verificar que incluye la estación creada
- [ ] Verificar que todos los campos están presentes

**Cantidad de estaciones:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.5 CRUD - Obtener Estación por ID (GET)

- [ ] **GET** `http://localhost:8000/api/estaciones/{id}`
- [ ] Verificar que retorna la estación correcta
- [ ] Verificar todos los campos: nombre, IP, puerto, precios, historial

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.6 CRUD - Actualizar Estación (PUT)

- [ ] **PUT** `http://localhost:8000/api/estaciones/{id}`
  ```json
  {
    "nombre": "Estación Test 1 - Actualizada",
    "estado": "Activa"
  }
  ```
- [ ] Verificar que el nombre cambió
- [ ] Verificar que `fecha_actualizacion` se modificó
- [ ] Verificar que los precios NO cambiaron

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.7 CRUD - Actualizar Precios (PUT)

- [ ] **PUT** `http://localhost:8000/api/estaciones/{id}/precios`
  ```json
  {
    "precios": {
      "precio_93": 1310,
      "precio_95": 1370,
      "precio_97": 1420,
      "precio_diesel": 1140
    }
  }
  ```
- [ ] Verificar que `precios_actuales` se actualizó
- [ ] Verificar que se agregó una entrada a `historico_precios`
- [ ] Verificar que el historial tiene timestamp
- [ ] Verificar campo `_envio_tcp` en la respuesta
- [ ] Anotar si `_envio_tcp.exitoso` es `true` o `false`

**Envío TCP exitoso:** [ ] Sí  [ ] No

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.8 CRUD - Obtener Historial (GET)

- [ ] **GET** `http://localhost:8000/api/estaciones/{id}/historico`
- [ ] Verificar que retorna un array
- [ ] Verificar que hay al menos 2 entradas (inicial + actualización)
- [ ] Verificar estructura de cada entrada: `timestamp` y `precios`

**Cantidad de entradas en historial:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.9 Validaciones - IP Duplicada

- [ ] Intentar crear otra estación con la misma IP
- [ ] Verificar que retorna error 400
- [ ] Verificar mensaje: "Ya existe una estación con la IP..."

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.10 Validaciones - Estación No Existe

- [ ] **GET** `http://localhost:8000/api/estaciones/99999`
- [ ] Verificar que retorna error 404
- [ ] **PUT** precios en ID inexistente
- [ ] Verificar que retorna error 404

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.11 Estadísticas del Sistema

- [ ] **GET** `http://localhost:8000/api/estadisticas`
- [ ] Verificar campos: `total_estaciones`, `activas`, `inactivas`, `desconectadas`
- [ ] Verificar que los números coinciden con la realidad

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 2.12 CRUD - Eliminar Estación (DELETE)

⚠️ **Nota:** Hacer esto al final para no perder datos de prueba

- [ ] **DELETE** `http://localhost:8000/api/estaciones/{id}`
- [ ] Verificar status 204 (No Content)
- [ ] Verificar que GET en ese ID retorna 404
- [ ] Verificar que la estación desapareció de la lista

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🖥️ FASE 3: Testing de Frontend - Gestión de Estaciones

### 3.1 Navegación

- [ ] Acceder a `http://localhost:3000`
- [ ] Verificar que el Navbar muestra: Dashboard, Gestión de Estaciones, Transacciones
- [ ] Click en "Gestión de Estaciones"
- [ ] Verificar que navega a `/estaciones`

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.2 Página de Gestión - Vista Inicial

- [ ] Verificar que se muestran las estaciones en formato grid/cards
- [ ] Verificar que cada card muestra: nombre, ID, IP, puerto, estado, precios
- [ ] Verificar que el badge de estado tiene el color correcto (verde=Activa)
- [ ] Verificar botón "Nueva Estación" visible

**Cantidad de estaciones mostradas:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.3 Crear Nueva Estación (Frontend)

- [ ] Click en "Nueva Estación"
- [ ] Verificar que se abre modal/dialog
- [ ] Llenar formulario:
  - Nombre: "Estación Frontend 1"
  - IP: "192.168.1.200"
  - Puerto: 5000
  - Precios: 1300, 1360, 1410, 1130
- [ ] Click "Crear Estación"
- [ ] Verificar que el modal se cierra
- [ ] Verificar que la nueva estación aparece en la lista
- [ ] Verificar que los datos son correctos

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.4 Editar Estación (Frontend)

- [ ] Click en botón "Editar" de una estación
- [ ] Verificar que se abre modal con datos precargados
- [ ] Cambiar el nombre a "Estación Frontend 1 - Editada"
- [ ] Click "Guardar Cambios"
- [ ] Verificar que el nombre se actualizó en la card
- [ ] Verificar que los precios NO cambiaron

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.5 Actualizar Precios (Frontend)

- [ ] Click en botón "Precios" (azul) de una estación
- [ ] Verificar que se abre modal con precios actuales
- [ ] Cambiar todos los precios (sumar +20 a cada uno)
- [ ] Click "Actualizar y Enviar"
- [ ] Verificar que aparece alert/mensaje
- [ ] Leer el mensaje: ¿dice que se enviaron exitosamente?
- [ ] Verificar que los precios se actualizaron en la card

**Mensaje recibido:**
```
_____________________________________________________________________________
```

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.6 Ver Historial (Frontend)

- [ ] Click en botón "📊 Historial" de una estación
- [ ] Verificar que navega a `/estaciones/{id}`
- [ ] Verificar que se muestra el timeline de cambios
- [ ] Verificar que la entrada más reciente tiene badge "Precios Actuales"
- [ ] Verificar que se muestran las diferencias (+/-) entre cambios
- [ ] Verificar que las fechas están en español y legibles
- [ ] Click "Volver a Estaciones"
- [ ] Verificar que regresa a la lista

**Cantidad de entradas en historial:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.7 Eliminar Estación (Frontend)

- [ ] Click en botón de eliminar (ícono de basura)
- [ ] Verificar que se abre modal de confirmación
- [ ] Leer mensaje de advertencia
- [ ] Click "Cancelar" - verificar que no pasa nada
- [ ] Volver a intentar eliminar
- [ ] Click "Eliminar"
- [ ] Verificar que la estación desaparece de la lista

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 3.8 Empty State

- [ ] Si no hay estaciones, verificar mensaje "No hay estaciones registradas"
- [ ] Verificar botón "Crear primera estación"

**Observaciones:**
```
_____________________________________________________________________________
```

### 3.9 Responsive Design

- [ ] Cambiar tamaño de ventana (simular móvil)
- [ ] Verificar que el grid se adapta (3 columnas → 2 → 1)
- [ ] Verificar que los modales funcionan en móvil
- [ ] Verificar que la navegación es usable

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🔄 FASE 4: Testing de Comunicación TCP (Empresa → Estación)

### 4.1 Preparación

- [ ] Tener Backend Estación corriendo en puerto 5000 (TCP)
- [ ] Tener `surtidor_simulado.py` corriendo
- [ ] Crear en Empresa una estación con IP: `127.0.0.1` y puerto: `5000`

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 4.2 Envío de Precios Manual (API)

- [ ] Actualizar precios de la estación (IP 127.0.0.1:5000) vía API
- [ ] Observar logs del Backend Estación
- [ ] Verificar mensaje: "💰 Actualización de precios recibida desde Empresa"
- [ ] Verificar mensaje: "✅ Precios actualizados: {...}"
- [ ] Verificar en la respuesta de la API: `_envio_tcp.exitoso: true`

**Logs observados:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 4.3 Propagación a Surtidor Simulado

- [ ] Observar logs de `surtidor_simulado.py`
- [ ] Verificar mensaje: "💰 Precios actualizados desde servidor: {...}"
- [ ] Verificar que en los siguientes envíos del surtidor, usa los nuevos precios
- [ ] Esperar 5 segundos (ciclo del surtidor)
- [ ] Verificar que el surtidor envía los precios actualizados

**Logs observados:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 4.4 Verificación en Frontend Estación

- [ ] Acceder al Frontend Estación (`http://localhost:3001`)
- [ ] Verificar que los precios se actualizaron en la interfaz
- [ ] Verificar que el cambio fue en tiempo real (vía WebSocket)

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 4.5 Testing con Estación Desconectada

- [ ] Detener el Backend Estación
- [ ] Intentar actualizar precios desde Empresa
- [ ] Verificar que la actualización se guarda en BD (historial)
- [ ] Verificar mensaje de error en respuesta: `_envio_tcp.exitoso: false`
- [ ] Verificar logs Backend Empresa: "❌ Conexión rechazada..."

**Logs observados:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 4.6 Reconexión

- [ ] Reiniciar Backend Estación
- [ ] Actualizar precios nuevamente desde Empresa
- [ ] Verificar que ahora sí llega el mensaje
- [ ] Verificar que `_envio_tcp.exitoso: true`

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🔍 FASE 5: Testing de Casos Extremos

### 5.1 Precios con Valores Extremos

- [ ] Crear estación con precios = 0
- [ ] Verificar que se acepta (validación >= 0)
- [ ] Intentar actualizar con precios negativos
- [ ] Verificar que se rechaza (error de validación)

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 5.2 Nombres Largos

- [ ] Crear estación con nombre de 200 caracteres
- [ ] Verificar que se acepta
- [ ] Verificar que se muestra correctamente en el frontend

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 5.3 IPs Inválidas

- [ ] Intentar crear con IP "abc.def.ghi.jkl"
- [ ] Verificar comportamiento (se guarda pero fallará TCP)
- [ ] Intentar actualizar precios
- [ ] Verificar `_envio_tcp.exitoso: false`

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 5.4 Puertos Fuera de Rango

- [ ] Intentar crear con puerto = 0
- [ ] Verificar error de validación (debe ser >= 1)
- [ ] Intentar puerto = 70000
- [ ] Verificar error de validación (debe ser <= 65535)

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 5.5 Múltiples Actualizaciones Rápidas

- [ ] Actualizar precios 5 veces seguidas muy rápido
- [ ] Verificar que todas se guardan en el historial
- [ ] Verificar que el historial tiene 5+ entradas
- [ ] Verificar orden cronológico

**Cantidad final en historial:** _______________

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 5.6 Múltiples Estaciones Simultáneas

- [ ] Crear 3 estaciones diferentes
- [ ] Actualizar precios de las 3 al mismo tiempo (diferentes pestañas)
- [ ] Verificar que todas se actualizan correctamente
- [ ] Verificar que no hay conflictos de IDs

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 📊 FASE 6: Testing de Rendimiento

### 6.1 Tiempo de Respuesta - API

- [ ] Medir tiempo de GET `/api/estaciones` con 1 estación
- [ ] Crear 10 estaciones
- [ ] Medir tiempo de GET `/api/estaciones` con 10 estaciones
- [ ] Medir tiempo de actualización de precios

**Tiempos medidos:**
- GET con 1 estación: _______ ms
- GET con 10 estaciones: _______ ms
- PUT precios: _______ ms

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### 6.2 Tamaño del Historial

- [ ] Actualizar precios 50 veces en una estación
- [ ] Verificar que el historial tiene 50+ entradas
- [ ] Medir tiempo de GET `/api/estaciones/{id}/historico`
- [ ] Verificar que el frontend muestra el timeline correctamente

**Tiempo GET historial:** _______ ms

**Observaciones:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🐛 FASE 7: Reporte de Bugs Encontrados

### Bug #1
**Descripción:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```
**Severidad:** [ ] Crítico  [ ] Alto  [ ] Medio  [ ] Bajo  
**Pasos para reproducir:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### Bug #2
**Descripción:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```
**Severidad:** [ ] Crítico  [ ] Alto  [ ] Medio  [ ] Bajo  
**Pasos para reproducir:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### Bug #3
**Descripción:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```
**Severidad:** [ ] Crítico  [ ] Alto  [ ] Medio  [ ] Bajo  
**Pasos para reproducir:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## ✅ FASE 8: Checklist Final

### Funcionalidades Core

- [ ] Crear estaciones funciona correctamente
- [ ] Listar estaciones funciona correctamente
- [ ] Actualizar estaciones funciona correctamente
- [ ] Actualizar precios funciona correctamente
- [ ] Eliminar estaciones funciona correctamente
- [ ] Ver historial funciona correctamente
- [ ] Envío TCP a estaciones funciona
- [ ] Propagación al surtidor funciona
- [ ] Frontend Estación recibe precios actualizados

### Validaciones y Errores

- [ ] Se validan IPs duplicadas
- [ ] Se validan precios >= 0
- [ ] Se validan puertos (1-65535)
- [ ] Se manejan errores de red (TCP)
- [ ] Se muestran mensajes de error al usuario

### UX/UI

- [ ] La navegación es intuitiva
- [ ] Los modales funcionan correctamente
- [ ] Los mensajes de confirmación son claros
- [ ] El diseño es responsive
- [ ] Los colores y estilos son consistentes

---

## 📋 Resumen Final

**Tests Totales:** _______  
**Tests Pasados:** _______  
**Tests Fallados:** _______  
**Bugs Críticos:** _______  
**Bugs No Críticos:** _______  

**Estado General:** [ ] ✅ Aprobado  [ ] ⚠️ Con observaciones  [ ] ❌ Rechazado

**Comentarios Generales:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

**Próximos Pasos Recomendados:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

---

**Firma del Tester:** _______________  
**Fecha:** _______________
