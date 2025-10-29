# 🔒 Guía de Seguridad - Identify Service

## ⚠️ **Vulnerabilidades Identificadas**

### **1. Endpoint `/auth/register` (Registro Directo)**

#### **Riesgos:**
- ✅ **Spam**: Creación de cuentas con emails falsos
- ✅ **Ataques de Fuerza Bruta**: Múltiples registros
- ✅ **Emails No Válidos**: Base de datos llena de datos inútiles
- ✅ **Sin Verificación**: No se valida que el email sea real

#### **Ejemplo de Ataque:**
```bash
# Atacante crea múltiples cuentas falsas
for i in {1..1000}; do
  curl -X POST http://localhost:8080/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"spam$i\", \"email\": \"spam$i@fake.com\", \"password\": \"Password123!\"}"
done
```

## 🛡️ **Soluciones Implementadas**

### **1. Configuración por Ambiente**

#### **Desarrollo (`application-dev.properties`):**
```properties
# Habilitar registro directo para desarrollo
app.registration.direct-enabled=true
app.registration.preregister-enabled=true
app.registration.oauth2-enabled=true
```

#### **Producción (`application-prod.properties`):**
```properties
# Deshabilitar registro directo en producción
app.registration.direct-enabled=false
app.registration.preregister-enabled=true
app.registration.oauth2-enabled=true
```

### **2. Control de Acceso**

#### **Registro Directo Deshabilitado:**
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
  }'

# Response 400
{
  "error": "Registro directo deshabilitado",
  "message": "Use /auth/preregister para registrarse con verificación de email",
  "status": "DISABLED"
}
```

### **3. Métodos de Registro Seguros**

#### **Preregistro con Verificación:**
```bash
# Método seguro para producción
curl -X POST http://localhost:8080/auth/preregister \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
  }'

# Response: Email de verificación enviado
{
  "message": "Preregistro exitoso",
  "status": "success",
  "email": "test@example.com",
  "note": "Revisa tu email para verificar tu cuenta"
}
```

#### **OAuth2 (Más Seguro):**
```bash
# Método más seguro - email ya verificado por Google
GET /oauth2/authorization/google
```

## 📊 **Comparación de Seguridad**

| Método | Verificación Email | Spam Protection | Recomendación |
|--------|-------------------|-------------------|----------------|
| **`/auth/register`** | ❌ No | ❌ No | ⚠️ Solo desarrollo |
| **`/auth/preregister`** | ✅ Sí | ✅ Sí | ✅ Producción |
| **OAuth2** | ✅ Sí (Google) | ✅ Sí | ✅ Producción |

## 🔧 **Configuración Recomendada**

### **Desarrollo:**
```bash
# Habilitar todos los métodos para testing
export REGISTRATION_DIRECT_ENABLED=true
export REGISTRATION_PREREGISTER_ENABLED=true
export REGISTRATION_OAUTH2_ENABLED=true
```

### **Producción:**
```bash
# Solo métodos seguros
export REGISTRATION_DIRECT_ENABLED=false
export REGISTRATION_PREREGISTER_ENABLED=true
export REGISTRATION_OAUTH2_ENABLED=true
```

## 🚨 **Medidas de Seguridad Adicionales**

### **1. Rate Limiting (Recomendado)**
```java
@RateLimiter(name = "register", fallbackMethod = "registerFallback")
@PostMapping("/register")
public ResponseEntity<Map<String, String>> register(@Valid @RequestBody RegisterRequest request) {
    // Implementación
}
```

### **2. CAPTCHA (Recomendado)**
```java
@PostMapping("/register")
public ResponseEntity<Map<String, String>> register(
    @Valid @RequestBody RegisterRequest request,
    @RequestParam String captchaToken) {
    
    // Verificar CAPTCHA
    if (!captchaService.verify(captchaToken)) {
        return ResponseEntity.badRequest().body(Map.of(
            "error", "CAPTCHA inválido",
            "message", "Por favor, completa el CAPTCHA"
        ));
    }
    
    // Continuar con registro
}
```

### **3. Validación de Email (Recomendado)**
```java
// Verificar que el dominio del email existe
if (!emailValidator.isValidDomain(request.getEmail())) {
    throw new IllegalArgumentException("Dominio de email no válido");
}
```

## 📋 **Checklist de Seguridad**

### **✅ Implementado:**
- [x] Configuración por ambiente
- [x] Deshabilitar registro directo en producción
- [x] Preregistro con verificación de email
- [x] OAuth2 con Google
- [x] Validación de datos de entrada
- [x] Encriptación de contraseñas

### **🔄 Recomendado Implementar:**
- [ ] Rate limiting
- [ ] CAPTCHA
- [ ] Validación de dominio de email
- [ ] Monitoreo de intentos de registro
- [ ] Alertas de seguridad
- [ ] Logs de auditoría

## 🎯 **Recomendaciones Finales**

### **Para Desarrollo:**
1. Usar `/auth/register` para testing rápido
2. Configurar `app.registration.direct-enabled=true`

### **Para Producción:**
1. **NUNCA** usar `/auth/register`
2. Usar `/auth/preregister` para usuarios normales
3. Usar OAuth2 para usuarios que prefieren Google
4. Configurar `app.registration.direct-enabled=false`

### **Para Testing:**
1. Usar emails reales para probar preregistro
2. Verificar que el flujo de email funciona
3. Probar expiración de tokens

---

**Nota**: El endpoint `/auth/register` se mantiene por compatibilidad y para desarrollo, pero debe estar deshabilitado en producción para evitar vulnerabilidades de seguridad.


