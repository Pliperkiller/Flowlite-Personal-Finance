# 📧 Guía de Preregistro con Verificación de Email

## 🎯 **Objetivo**
Implementar un sistema de preregistro que requiere verificación de email antes de completar el registro del usuario, mejorando la seguridad y validando la autenticidad de las cuentas.

## 🔄 **Flujo de Preregistro**

### **1. Flujo Completo:**
```
Usuario → Preregistro → Email de Verificación → Verificación → Registro Final → Login
```

### **2. Pasos Detallados:**

#### **Paso 1: Preregistro**
- Usuario envía datos (username, email, password)
- Sistema valida datos y crea `PendingUser`
- Se envía email de verificación
- Usuario NO puede hacer login aún

#### **Paso 2: Verificación de Email**
- Usuario hace clic en enlace del email
- Sistema valida token y crea `User` final
- Se elimina `PendingUser`
- Usuario puede hacer login

## 🏗️ **Arquitectura Implementada**

### **Nuevos Componentes (Sin modificar existentes):**

#### **1. Entidades:**
- **`PendingUserData`** - Usuarios pendientes de verificación (Redis)
- **`User`** - Usuarios finales (existente, sin cambios)

#### **2. DTOs:**
- **`PreregisterRequest`** - Datos para preregistro
- **`VerificationRequest`** - Token de verificación

#### **3. Servicios:**
- **`PreregisterUserService`** - Lógica de preregistro
- **`EmailService`** - Envío de emails
- **`RegisterUserService`** - Registro final (existente)

#### **4. Repositorios:**
- **`PendingUserRedisRepository`** - Gestión de usuarios pendientes en Redis
- **`UserRepository`** - Usuarios finales (existente, sin cambios)

#### **5. Controladores:**
- **`VerificationController`** - Endpoints de preregistro
- **`AuthController`** - Login/Logout (existente)

## 📋 **Endpoints Disponibles**

### **1. POST /auth/preregister**
**Preregistro de usuario con verificación de email**

```json
// Request
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "Password123!"
}

// Response (200)
{
  "message": "Preregistro exitoso",
  "status": "success",
  "email": "john@example.com",
  "note": "Revisa tu email para verificar tu cuenta. El enlace será válido por 24 horas."
}
```

### **2. POST /auth/verify**
**Verificar email y completar registro**

```json
// Request
{
  "token": "uuid-verification-token"
}

// Response (200)
{
  "message": "Email verificado exitosamente",
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### **3. GET /auth/verify?token=xxx**
**Verificar email desde enlace (para emails)**

```json
// Response (200)
{
  "message": "Email verificado exitosamente",
  "status": "success",
  "redirect": "http://localhost:3000/verification-success"
}
```

## 🔒 **Validaciones Implementadas**

### **Preregistro:**
- ✅ Username único (no existe en `User` ni `PendingUser`)
- ✅ Email único (no existe en `User` ni `PendingUser`)
- ✅ Password con caracteres especiales
- ✅ Validación de formato de email

### **Verificación:**
- ✅ Token válido y no expirado
- ✅ Token no usado previamente
- ✅ Expiración de 24 horas

## 📊 **Almacenamiento de Datos**

### **Redis para Usuarios Pendientes:**
- **`PendingUserData`** almacenado en Redis con TTL automático
- **Claves Redis:**
  - `pending_user:{token}` - Datos del usuario pendiente
  - `pending_email:{email}` - Índice por email
  - `pending_username:{username}` - Índice por username
  - `pending_token:{token}` - Índice por token

### **MySQL para Usuarios Finales:**
- **`User`** almacenado en MySQL (sin cambios)
- Tabla `users` existente

### **Ventajas de Redis:**
- ✅ **TTL Automático**: Los tokens expiran automáticamente en 24 horas
- ✅ **Performance**: Acceso ultra-rápido a datos temporales
- ✅ **Simplicidad**: No necesita limpieza manual
- ✅ **Memoria**: Libera espacio automáticamente
- ✅ **Escalabilidad**: Mejor para datos temporales

## ⚙️ **Configuración de Email**

### **Variables de Entorno:**
```bash
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
APP_EMAIL_FROM=noreply@flowlite.com
APP_EMAIL_VERIFICATION_URL=http://localhost:8080/auth/verify
```

### **Gmail Setup:**
1. Habilitar autenticación de 2 factores
2. Generar contraseña de aplicación
3. Usar contraseña de aplicación en `MAIL_PASSWORD`

## 🧪 **Casos de Prueba**

### **✅ Flujo Exitoso:**
```bash
# 1. Preregistro
curl -X POST http://localhost:8080/auth/preregister \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# 2. Verificación (usar token del email)
curl -X POST http://localhost:8080/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "uuid-from-email"
  }'
```

### **❌ Casos de Error:**
```bash
# Email ya registrado
curl -X POST http://localhost:8080/auth/preregister \
  -H "Content-Type: application/json" \
  -d '{
    "username": "existinguser",
    "email": "existing@example.com",
    "password": "TestPass123!"
  }'

# Token expirado
curl -X POST http://localhost:8080/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "expired-token"
  }'
```

## 🔄 **Migración del Sistema Existente**

### **Compatibilidad:**
- ✅ **Registro directo** (`/auth/register`) sigue funcionando
- ✅ **Login** (`/auth/login`) sin cambios
- ✅ **Logout** (`/auth/logout`) sin cambios
- ✅ **Validación de tokens** sin cambios

### **Nuevas Funcionalidades:**
- 🆕 **Preregistro** (`/auth/preregister`)
- 🆕 **Verificación** (`/auth/verify`)
- 🆕 **Limpieza automática** de tokens expirados

## 📈 **Beneficios Implementados**

1. **Seguridad**: Verificación de email real
2. **Calidad de datos**: Emails válidos y activos
3. **Prevención de spam**: Dificulta cuentas falsas
4. **Experiencia**: Flujo claro y guiado
5. **Mantenimiento**: Limpieza automática de datos temporales

## 🚀 **Próximos Pasos**

1. **Configurar SMTP** con credenciales reales
2. **Personalizar templates** de email
3. **Implementar reenvío** de emails
4. **Agregar métricas** de conversión
5. **Testing** con emails reales
6. **Monitoreo Redis** para tokens pendientes

---

**Nota**: Este sistema extiende la funcionalidad existente sin modificar el comportamiento actual, manteniendo la compatibilidad total con el sistema de registro directo.
