# Guía Rápida para Windows - Migración UserInfo

Si estás usando **Windows + Git Bash** y tienes el error:
```
Unknown column 'uie1_0.id' in 'field list'
```

Esta guía te ayudará a solucionarlo en **3 pasos simples**.

---

## 🚀 Solución Rápida (3 Pasos)

### Paso 1: Asegúrate de que Docker Desktop esté corriendo

1. **Abre Docker Desktop** desde el menú inicio de Windows
2. **Espera** a que el ícono muestre "Docker Desktop is running"
3. **Verifica** en Git Bash:
   ```bash
   docker ps
   ```
   Si ves una tabla (aunque esté vacía), está funcionando ✅

---

### Paso 2: Verifica si la migración se aplicó

En Git Bash, ejecuta:

```bash
cd /c/Users/Usuario/Documents/Flowlite-Personal-Finance/database
./check-migration.sh
```

**Posibles resultados:**

**✅ Si dice "Migración APLICADA":**
- ¡Perfecto! Solo reinicia el servicio:
  ```bash
  cd ../identifyservice
  ./kill.sh
  ./start.sh
  ```

**❌ Si dice "Migración PENDIENTE":**
- Continúa al Paso 3

---

### Paso 3: Aplica la migración manualmente

En Git Bash, ejecuta:

```bash
cd /c/Users/Usuario/Documents/Flowlite-Personal-Finance/database
./apply-migration-manually.sh
```

Este script:
- ✅ Detecta automáticamente tu contenedor MySQL
- ✅ Detecta automáticamente las credenciales
- ✅ Aplica la migración a la base de datos
- ✅ Te dice exactamente qué hacer después

**Deberías ver:**
```
✓✓✓ ÉXITO ✓✓✓

La tabla UserInfo ahora tiene la estructura correcta
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      ✨ MIGRACIÓN COMPLETADA ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ Próximos pasos:

  1️⃣  Reinicia el IdentityService:
     cd identifyservice && ./kill.sh && ./start.sh
```

---

## 🎯 Resumen Ultra Rápido

```bash
# 1. Asegúrate de que Docker Desktop esté corriendo

# 2. Verifica migración
cd /c/Users/Usuario/Documents/Flowlite-Personal-Finance/database
./check-migration.sh

# 3. Si dice PENDIENTE, aplícala:
./apply-migration-manually.sh

# 4. Reinicia el servicio
cd ../identifyservice
./kill.sh
./start.sh

# 5. ¡Listo! Prueba el endpoint /user-info/update
```

---

## 🔍 ¿Qué hace la migración?

La migración arregla la tabla `UserInfo` para que pueda almacenar UUIDs correctamente:

**ANTES (❌ Error):**
```sql
CREATE TABLE UserInfo (
    id_user VARCHAR(255) PRIMARY KEY,  -- ❌ No puede almacenar UUIDs
    ...
);
```

**DESPUÉS (✅ Funciona):**
```sql
CREATE TABLE UserInfo (
    id BINARY(16) PRIMARY KEY,          -- ✅ ID propio
    id_user BINARY(16) UNIQUE,          -- ✅ Referencia al usuario
    ...
);
```

Esto soluciona el error:
```
Incorrect string value: '\xDC\x1C\xBCw\xEA\xEF...' for column 'id_user'
```

---

## ❓ Problemas Comunes

### "Docker no está disponible"

**Solución:**
1. Abre Docker Desktop desde el menú inicio
2. Espera a que inicie completamente
3. Ejecuta `docker ps` para verificar

---

### "No se encontró ningún contenedor MySQL"

**Solución:**
```bash
# Inicia MySQL
cd /c/Users/Usuario/Documents/Flowlite-Personal-Finance/infrastructureservice
docker-compose up -d mysql

# Espera 10 segundos
sleep 10

# Intenta de nuevo
cd ../database
./apply-migration-manually.sh
```

---

### "Permission denied" al ejecutar scripts

**Solución:**
```bash
# Dale permisos de ejecución
chmod +x database/*.sh

# Intenta de nuevo
./apply-migration-manually.sh
```

---

## 📞 Ayuda Adicional

Si nada de esto funciona:

1. **Ver logs de MySQL:**
   ```bash
   docker logs flowlite-mysql
   ```

2. **Ejecutar migración manualmente (Plan B):**
   ```bash
   # Conectarse a MySQL
   docker exec -it flowlite-mysql mysql -uroot -prootpassword flowlite_db

   # Copiar y pegar el contenido de:
   # database/migrations/001_fix_userinfo_structure.sql
   ```

3. **Revisar documentación completa:**
   - `database/MIGRATIONS_README.md`
   - `identifyservice/MIGRATION_USERINFO_README.md`

---

## ✅ Verificación Final

Después de aplicar la migración, verifica:

```bash
# Ver estructura de UserInfo
docker exec flowlite-mysql mysql -uroot -prootpassword flowlite_db -e "DESCRIBE UserInfo;"
```

Debes ver:
- ✅ Columna `id` (BINARY(16), PRI)
- ✅ Columna `id_user` (BINARY(16), UNI)
- ✅ Todas las demás columnas

**Si ves esto, ¡está todo correcto!** 🎉

El endpoint `/user-info/update` ahora debería funcionar sin errores.
