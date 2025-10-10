# Guía de Testing - Servicio de Transacciones

## Usuarios de Prueba Disponibles

Después de ejecutar `python scripts/init_db.py`, tendrás estos usuarios:

```
┌─────────────────────────────────────────────────────────────┐
│                   USUARIOS DE PRUEBA                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Juan Pérez                                               │
│    Email: test1@example.com                                 │
│    Password: password123                                    │
│    User ID: 1                                               │
│                                                             │
│ 2. María González                                           │
│    Email: test2@example.com                                 │
│    Password: password123                                    │
│    User ID: 2                                               │
│                                                             │
│ 3. Carlos Rodríguez                                         │
│    Email: test3@example.com                                 │
│    Password: password123                                    │
│    User ID: 3                                               │
│                                                             │
│ 4. Admin Sistema                                            │
│    Email: admin@example.com                                 │
│    Password: admin123                                       │
│    User ID: 4                                               │
└─────────────────────────────────────────────────────────────┘
```

## Flujo Completo de Testing

### Paso 1: Configuración Inicial

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# 2. Iniciar servicios
docker-compose up -d

# O si usas Python local:
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# uvicorn src.main:app --reload
```

### Paso 2: Inicializar Base de Datos

```bash
python scripts/init_db.py
```

**Salida esperada:**
```
============================================================
Datos iniciales creados exitosamente
============================================================

Usuarios de prueba creados:
------------------------------------------------------------
1. Email: test1@example.com
   Nombre: Juan Pérez
   Password: password123
   ID en DB: 1

2. Email: test2@example.com
   Nombre: María González
   Password: password123
   ID en DB: 2

[...]
============================================================
```

### Paso 3: Generar Tokens JWT

```bash
python scripts/generate_test_tokens.py
```

**Salida esperada:**
```
================================================================================
TOKENS JWT DE PRUEBA
================================================================================
SecretKey: your-secret-key-here
Algorithm: HS256
Expiración: 30 días

================================================================================

Usuario: Juan Pérez (test1@example.com)
User ID: 1
Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoidGVzdDFAZXhhbXBsZS5jb20iLCJleHAiOjE3MzE1MjAwMDAsImlhdCI6MTcyODkyODAwMH0...
--------------------------------------------------------------------------------

[...]
```

Copia el token del usuario que quieras usar.

### Paso 4: Pruebas de Endpoints

#### 4.1. Health Check (sin autenticación)

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

#### 4.2. Verificar Token (con autenticación)

```bash
export TOKEN="tu-token-aqui"

curl -X GET "http://localhost:8000/api/v1/test/user-id" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "user_id": 1,
  "message": "El token corresponde al usuario con ID 1"
}
```

#### 4.3. Cargar Archivo de Transacciones

```bash
curl -X POST "http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCOLOMBIA" \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivos=@MovimientosTusCuentasBancolombia07Oct2025.xlsx"
```

**Respuesta esperada:**
```json
{
  "lote_id": 1,
  "message": "Procesamiento iniciado. Use el lote_id 1 para consultar el estado."
}
```

#### 4.4. Consultar Estado del Lote

```bash
# Inmediatamente después de cargar
curl -X GET "http://localhost:8000/api/v1/transacciones/lote/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (procesando):**
```json
{
  "lote_id": 1,
  "estado": "procesando",
  "total_registros": 190,
  "registros_procesados": 95,
  "porcentaje_procesado": 50.0,
  "created_at": "2025-10-10T10:00:00.000000",
  "updated_at": "2025-10-10T10:00:30.000000"
}
```

**Respuesta esperada (completado):**
```json
{
  "lote_id": 1,
  "estado": "completado",
  "total_registros": 190,
  "registros_procesados": 190,
  "porcentaje_procesado": 100.0,
  "created_at": "2025-10-10T10:00:00.000000",
  "updated_at": "2025-10-10T10:01:00.000000"
}
```

### Paso 5: Verificar en Base de Datos (Opcional)

```bash
# Conectar a MySQL
mysql -u user -p transactions_db

# Ver usuarios
SELECT id, email, nombre, apellido FROM usuarios;

# Ver bancos
SELECT * FROM bancos;

# Ver categorías
SELECT * FROM categorias;

# Ver lotes creados
SELECT * FROM lotes_transaccion;

# Ver transacciones procesadas
SELECT COUNT(*) as total FROM transacciones WHERE lote_id = 1;

# Ver distribución por categorías
SELECT c.nombre, COUNT(*) as cantidad
FROM transacciones t
JOIN categorias c ON t.categoria_id = c.id
WHERE t.lote_id = 1
GROUP BY c.nombre;
```

## Casos de Prueba

### ✅ Caso 1: Usuario Válido Carga Archivo
- **Usuario:** test1@example.com (ID: 1)
- **Archivo:** MovimientosTusCuentasBancolombia07Oct2025.xlsx
- **Resultado Esperado:** Lote creado exitosamente

### ✅ Caso 2: Token Inválido
```bash
curl -X GET "http://localhost:8000/api/v1/test/user-id" \
  -H "Authorization: Bearer token-invalido"
```
**Resultado Esperado:** 401 Unauthorized

### ✅ Caso 3: Sin Token
```bash
curl -X GET "http://localhost:8000/api/v1/test/user-id"
```
**Resultado Esperado:** 401 Unauthorized

### ✅ Caso 4: Banco No Soportado
```bash
curl -X POST "http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCO_INEXISTENTE" \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivos=@archivo.xlsx"
```
**Resultado Esperado:** 400 Bad Request

### ✅ Caso 5: Consultar Lote de Otro Usuario
- **Usuario 1:** Crea lote_id=1
- **Usuario 2:** Intenta consultar lote_id=1
**Resultado Esperado:** 403 Forbidden

### ✅ Caso 6: Múltiples Archivos del Mismo Banco
```bash
curl -X POST "http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCOLOMBIA" \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivos=@archivo1.xlsx" \
  -F "archivos=@archivo2.xlsx"
```
**Resultado Esperado:** Lote único con todas las transacciones

## Documentación Interactiva

Visita `http://localhost:8000/docs` para acceder a Swagger UI donde podrás:
- Ver todos los endpoints
- Probar requests directamente desde el navegador
- Ver esquemas de datos
- Autorizar con tu token JWT

## Troubleshooting

### Error: "Could not validate credentials"
- Verifica que el token sea correcto
- Verifica que `JWT_SECRET_KEY` en `.env` coincida con el usado para generar el token
- Genera un nuevo token con `python scripts/generate_test_tokens.py`

### Error: "Banco con código X no encontrado"
- Ejecuta `python scripts/init_db.py` para crear los bancos
- Verifica que el código del banco esté en mayúsculas

### Error: Base de datos no conecta
- Verifica que MySQL esté corriendo
- Verifica las credenciales en `DATABASE_URL` en `.env`
- Si usas Docker: `docker-compose logs mysql`

### Error: Tabla usuarios no existe
- Ejecuta `python scripts/init_db.py`
- Verifica que las migraciones se hayan ejecutado correctamente
