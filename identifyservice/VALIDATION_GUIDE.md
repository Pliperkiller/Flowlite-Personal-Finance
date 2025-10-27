# 🔒 Guía de Validación de Campos - Identify Service

## 📋 Resumen

Este servicio ahora incluye validaciones robustas para todos los endpoints que reciben datos del usuario. Cuando se envían campos faltantes o con formato inválido, el servicio devuelve un **error 400 (Bad Request)** con mensajes descriptivos.

## 🚀 Endpoints con Validación

### 1. **POST /auth/register** - Registro de Usuario

#### Campos Requeridos:
- **username** (obligatorio)
  - No puede estar vacío
  - Debe tener entre 3 y 50 caracteres
  - Solo puede contener letras, números y guiones bajos
  - Ejemplo válido: `johndoe123`

- **email** (obligatorio)
  - No puede estar vacío
  - Debe tener formato de email válido
  - Máximo 100 caracteres
  - Ejemplo válido: `john@example.com`

- **password** (obligatorio)
  - No puede estar vacío
  - Debe tener entre 8 y 128 caracteres
  - Debe contener al menos:
    - Una letra minúscula
    - Una letra mayúscula
    - Un número
    - Un carácter especial (!@#$%^&*(),.?":{}|<>)
  - Ejemplo válido: `Password123!`

#### Ejemplo de Request Válido:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "Password123!"
}
```

#### Ejemplo de Response de Error 400:
```json
{
  "error": "Error de validación",
  "message": "Los campos requeridos no pueden estar vacíos o tienen formato inválido",
  "details": {
    "username": "El nombre de usuario es obligatorio",
    "email": "El formato del email no es válido",
    "password": "La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial"
  },
  "status": "BAD_REQUEST"
}
```

### 2. **POST /auth/login** - Inicio de Sesión

#### Campos Requeridos:
- **username** (obligatorio)
  - No puede estar vacío
  - Debe tener entre 3 y 50 caracteres

- **password** (obligatorio)
  - No puede estar vacío
  - Debe tener entre 8 y 128 caracteres

#### Ejemplo de Request Válido:
```json
{
  "username": "johndoe",
  "password": "MyPassword123!"
}
```

#### Ejemplo de Response de Error 400:
```json
{
  "error": "Error de validación",
  "message": "Los campos requeridos no pueden estar vacíos o tienen formato inválido",
  "details": {
    "username": "El nombre de usuario es obligatorio",
    "password": "La contraseña debe tener entre 8 y 128 caracteres"
  },
  "status": "BAD_REQUEST"
}
```

## 🔧 Implementación Técnica

### 1. **Anotaciones de Validación**
Los DTOs utilizan las siguientes anotaciones de Jakarta Validation:

```java
@NotBlank(message = "El campo es obligatorio")
@Size(min = 3, max = 50, message = "Debe tener entre 3 y 50 caracteres")
@Email(message = "El formato del email no es válido")
@Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "Solo letras, números y guiones bajos")
```

### 2. **Manejador Global de Excepciones**
El `GlobalExceptionHandler` captura automáticamente:
- `MethodArgumentNotValidException` - Violaciones de validación
- `IllegalArgumentException` - Argumentos inválidos
- `Exception` - Errores generales

### 3. **Configuración de Validación**
- Mensajes personalizados en `validation-messages.properties`
- Configuración en `ValidationConfig.java`
- Integración con Spring Boot Validation

## 📊 Códigos de Respuesta

| Código | Descripción | Cuándo Ocurre |
|--------|-------------|---------------|
| **200** | Éxito | Validación pasada, operación exitosa |
| **400** | Bad Request | Campos faltantes o formato inválido |
| **401** | Unauthorized | Credenciales inválidas (solo en login) |
| **500** | Internal Server Error | Error interno del servidor |

## 🧪 Casos de Prueba

### ✅ **Casos Válidos**
```bash
# Registro exitoso
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Login exitoso
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### ❌ **Casos de Error 400**
```bash
# Campos faltantes
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "",
    "email": "invalid-email",
    "password": "123"
  }'

# Formato inválido
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ab",
    "password": ""
  }'
```

## 🔍 Monitoreo y Debugging

### Logs de Validación
Los errores de validación se registran automáticamente en los logs con:
- Timestamp del error
- Detalles de la validación fallida
- Stack trace para debugging

### Swagger/OpenAPI
La documentación de Swagger incluye:
- Ejemplos de requests válidos
- Ejemplos de responses de error
- Descripción detallada de cada campo

## 🚀 Próximos Pasos

1. **Validaciones Adicionales**: Agregar validaciones para otros endpoints
2. **Rate Limiting**: Implementar límites de intentos de login
3. **Auditoría**: Registrar intentos de validación fallidos
4. **Internacionalización**: Soporte para múltiples idiomas

---

**Nota**: Todas las validaciones se ejecutan antes de procesar la lógica de negocio, garantizando que solo se procesen datos válidos y completos.
