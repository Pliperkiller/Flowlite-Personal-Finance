# Control de Versiones del Seed - Flowlite

## 📋 Problema Identificado

### Síntoma
A pesar de actualizar el archivo `scripts/seed_database.py` con nuevas categorías ML (con underscores como `Servicios_Publicos`), la base de datos se cargaba con categorías antiguas (con espacios como "Servicios Públicos").

### Causa Raíz
Docker cachea las imágenes construidas. Cuando se ejecutaba `docker-compose up`, Docker usaba una **imagen antigua** del servicio `db-init` que contenía el código desactualizado del seed, en lugar de reconstruir la imagen con el código más reciente.

### Impacto
- El clasificador ML no encontraba las categorías correctas
- Las transacciones no se clasificaban adecuadamente
- Los desarrolladores nuevos o que hacían `git pull` tenían datos inconsistentes

---

## ✅ Soluciones Implementadas

### 1. Script de Setup Automático (`setup.sh`)

**Ubicación:** `/infrastructureservice/setup.sh`

**Qué hace:**
- ✅ Detecta y elimina imágenes Docker antiguas automáticamente
- ✅ Reconstruye la imagen `db-init` sin caché
- ✅ Inicializa y valida la base de datos
- ✅ Verifica que las categorías ML estén correctamente cargadas

**Uso:**
```bash
cd infrastructureservice
./setup.sh
```

**Cuándo usarlo:**
- Primera vez que configuras el proyecto
- Después de hacer `git pull` con cambios en `seed_database.py`
- Cuando sospeches que tienes datos desactualizados
- Para limpiar y reiniciar desde cero

---

### 2. Versionado de Imagen en docker-compose.yml

**Cambios realizados:**
```yaml
db-init:
  build:
    context: .
    dockerfile: Dockerfile.init
    args:
      SEED_VERSION: "20251105-ml-categories"  # 👈 Nueva versión
  image: infrastructureservice-db-init:${SEED_VERSION:-latest}  # 👈 Tag con versión
  environment:
    SEED_VERSION: ${SEED_VERSION:-20251105-ml-categories}  # 👈 Variable de entorno
```

**Cómo funciona:**
- Cada vez que cambias `SEED_VERSION`, Docker crea una nueva imagen con un tag diferente
- Esto fuerza a Docker a reconstruir en lugar de usar caché
- La versión se muestra en los logs para debugging

**Cuándo actualizar la versión:**
- Al modificar `scripts/seed_database.py` significativamente
- Al cambiar estructura de categorías
- Al agregar/eliminar datos de prueba importantes

**Formato sugerido de versión:**
- `YYYYMMDD-descripcion` (ej: `20251105-ml-categories`)
- `YYYYMMDD-HH` (ej: `20251105-02`)
- `v1.x.x` (ej: `v1.2.0`)

---

### 3. Build Argument en Dockerfile.init

**Cambios realizados:**
```dockerfile
FROM python:3.11-slim

# Aceptar versión del seed como build argument
ARG SEED_VERSION=unknown
ENV SEED_VERSION=${SEED_VERSION}

# ... resto del Dockerfile ...

# Agregar un archivo con la versión para debugging
RUN echo "SEED_VERSION=${SEED_VERSION}" > /app/build_info.txt && \
    echo "BUILD_DATE=$(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> /app/build_info.txt
```

**Beneficios:**
- La versión está "grabada" en la imagen
- Se puede consultar con: `docker exec flowlite-db-init cat /app/build_info.txt`
- Facilita el debugging de problemas de versión

---

### 4. Validación Automática en seed_database.py

**Cambios realizados:**
```python
# Al inicio del script
seed_version = os.getenv('SEED_VERSION', 'unknown')
if seed_version != 'unknown':
    logger.info(f"Seed Version: {seed_version}")

# Al final del script
logger.info("VALIDACIÓN DE CATEGORÍAS ML")
category_count = session.query(TransactionCategory).count()
expected_count = 11

if category_count == expected_count:
    ml_categories = session.query(TransactionCategory).filter(
        TransactionCategory.description.like('%\_%')
    ).count()

    if ml_categories >= 10:
        logger.info(f"✓ Categorías con formato ML detectadas: {ml_categories}")
    else:
        logger.warning("⚠ Las categorías pueden no ser compatibles con el clasificador ML")
```

**Beneficios:**
- Detecta automáticamente si se cargaron las categorías incorrectas
- Muestra warnings visibles en los logs
- Previene errores silenciosos

---

### 5. Documentación Actualizada

**README.md actualizado con:**
- Sección "Quick Start" prominente que recomienda usar `setup.sh`
- Advertencia clara sobre el problema de imágenes antiguas
- Síntomas del problema para fácil identificación
- Instrucciones de solución manual alternativa
- Sección de control de versiones del seed

---

## 🔍 Verificación

### Verificar que tienes la versión correcta:

```bash
# 1. Ver versión en docker-compose
grep "SEED_VERSION:" infrastructureservice/docker-compose.yml

# 2. Ver versión en la imagen corriendo
docker exec flowlite-db-init cat /app/build_info.txt

# 3. Ver logs del seed
docker logs flowlite-db-init | grep "Seed Version"

# 4. Verificar categorías en la base de datos
docker exec flowlite-mysql mysql -u flowlite_user -pflowlite_password flowlite_db \
  -e "SELECT id_category, description FROM TransactionCategory ORDER BY id_category;"
```

**Salida esperada (11 categorías con underscores):**
```
cat-001-retiros-efectivo              → Retiros_Efectivo
cat-002-alimentacion-restaurantes     → Alimentacion_Restaurantes
cat-003-supermercados-hogar          → Supermercados_Hogar
cat-004-combustible-transporte       → Combustible_Transporte
cat-005-entretenimiento              → Entretenimiento
cat-006-servicios-publicos           → Servicios_Publicos
cat-007-vivienda-arriendo            → Vivienda_Arriendo
cat-008-salud-cuidado-personal       → Salud_Cuidado_Personal
cat-009-educacion                    → Educacion
cat-010-obligaciones-financieras     → Obligaciones_Financieras
cat-011-transferencias-ingresos      → Transferencias_Ingresos
```

---

## 🚨 Troubleshooting

### Problema: "Todavía veo las categorías antiguas"

**Solución:**
```bash
cd infrastructureservice

# Limpiar todo forzosamente
docker-compose down
docker rmi -f $(docker images | grep infrastructureservice-db-init | awk '{print $3}')
docker volume rm $(docker volume ls -q | grep flowlite) 2>/dev/null || true

# Rebuild desde cero
./setup.sh
```

### Problema: "El script setup.sh no tiene permisos"

**Solución:**
```bash
chmod +x infrastructureservice/setup.sh
```

### Problema: "Docker dice 'image not found'"

**Solución:**
```bash
cd infrastructureservice
docker-compose build --no-cache db-init
docker-compose up -d
```

### Problema: "Las categorías están correctas pero el clasificador falla"

**Verificar:**
1. Que el modelo ML esté entrenado con las mismas categorías
2. Que `uploadservice/models/metadata.json` tenga la lista correcta
3. Revisar logs del clasificador: `docker logs flowlite-upload-service`

---

## 📝 Workflow para Desarrolladores

### Al hacer cambios en el seed:

1. **Modificar** `scripts/seed_database.py`
2. **Actualizar versión** en `docker-compose.yml`:
   ```yaml
   SEED_VERSION: "20251105-02"  # Incrementar
   ```
3. **Ejecutar setup:**
   ```bash
   ./setup.sh
   ```
4. **Verificar cambios:**
   ```bash
   docker logs flowlite-db-init | tail -30
   ```
5. **Commit ambos archivos:**
   ```bash
   git add scripts/seed_database.py docker-compose.yml
   git commit -m "feat(seed): actualizar categorías a versión 20251105-02"
   ```

### Al hacer git pull:

```bash
cd infrastructureservice
./setup.sh  # Siempre usa setup después de pull
```

---

## 📚 Recursos Adicionales

- **Logs de db-init:** `docker logs flowlite-db-init`
- **Logs en tiempo real:** `docker-compose logs -f db-init`
- **Entrar al contenedor:** `docker exec -it flowlite-mysql bash`
- **Verificar infraestructura:** `python scripts/check_infrastructure.py`

---

## 🎯 Conclusión

Este sistema de versionado garantiza que:
- ✅ Todos los desarrolladores usen los mismos datos de prueba
- ✅ No haya confusión con imágenes Docker antiguas
- ✅ Los cambios en el seed sean trazables
- ✅ El setup sea automatizado y a prueba de errores

**Regla de oro:** Siempre ejecuta `./setup.sh` después de hacer `git pull` o cuando tengas dudas sobre tus datos.
