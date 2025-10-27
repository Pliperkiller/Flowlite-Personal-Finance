# MailHog - Servicio de Correo para Desarrollo

MailHog es un servidor SMTP de desarrollo que captura todos los emails enviados por tu aplicación, permitiendo verlos en una interfaz web sin enviar emails reales.

## 🚀 Inicio Rápido

### Iniciar MailHog
```bash
# Linux/macOS
./manage-mailhog.sh start

# Windows
manage-mailhog.bat start
```

### Acceder a la Interfaz Web
- **URL**: http://localhost:8025
- **SMTP**: localhost:1025

## 📋 Comandos Disponibles

### Linux/macOS
```bash
./manage-mailhog.sh [comando]
```

### Windows
```cmd
manage-mailhog.bat [comando]
```

**Comandos disponibles:**
- `start` - Iniciar MailHog
- `stop` - Detener MailHog
- `restart` - Reiniciar MailHog
- `status` - Ver estado de MailHog
- `logs` - Ver logs de MailHog
- `clean` - Limpiar datos de MailHog
- `web` - Abrir interfaz web de MailHog
- `check` - Verificar configuración
- `help` - Mostrar ayuda

## 🔧 Configuración para identifyservice

Para usar MailHog con tu servicio de identificación, actualiza las variables de entorno:

```bash
# Variables de entorno para identifyservice
export MAIL_HOST=localhost
export MAIL_PORT=1025
export MAIL_USERNAME=
export MAIL_PASSWORD=
```

O actualiza el archivo `application.properties`:

```properties
spring.mail.host=localhost
spring.mail.port=1025
spring.mail.username=
spring.mail.password=
```

## 🌐 Interfaz Web

La interfaz web de MailHog te permite:
- ✅ Ver todos los emails enviados
- ✅ Ver contenido HTML y texto plano
- ✅ Ver headers y metadatos
- ✅ Descargar emails
- ✅ Buscar emails
- ✅ Eliminar emails individuales

## 📊 Características

### ✅ Ventajas
- **Gratuito** - Sin límites de uso
- **Local** - No requiere internet
- **Seguro** - No envía emails reales
- **Fácil** - Configuración mínima
- **Visual** - Interfaz web intuitiva

### 🎯 Casos de Uso
- **Desarrollo** - Testing de emails sin spam
- **Debugging** - Verificar contenido de emails
- **Demo** - Mostrar funcionalidad de correo
- **CI/CD** - Testing automatizado

## 🔍 Monitoreo

### Verificar Estado
```bash
./manage-mailhog.sh status
```

### Ver Logs
```bash
./manage-mailhog.sh logs
```

### Verificar Puertos
```bash
./manage-mailhog.sh check
```

## 🧹 Limpieza

### Limpiar Datos
```bash
./manage-mailhog.sh clean
```

Esto eliminará:
- Todos los emails capturados
- Volúmenes de Docker
- Datos persistentes

## 🐳 Docker

MailHog se ejecuta en un contenedor Docker con:
- **Imagen**: `mailhog/mailhog:latest`
- **Puerto SMTP**: 1025
- **Puerto Web**: 8025
- **Almacenamiento**: Volumen persistente

## 🔧 Configuración Avanzada

### Variables de Entorno
```yaml
environment:
  - MH_STORAGE=maildir
  - MH_MAILDIR_PATH=/maildir
```

### Red Docker
```yaml
networks:
  - flowlite-network
```

### Health Check
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8025"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🚨 Solución de Problemas

### Puerto en Uso
```bash
# Verificar puertos
./manage-mailhog.sh check

# Cambiar puertos en docker-compose.yml si es necesario
```

### Contenedor No Inicia
```bash
# Ver logs
./manage-mailhog.sh logs

# Reiniciar
./manage-mailhog.sh restart
```

### Datos Corruptos
```bash
# Limpiar y reiniciar
./manage-mailhog.sh clean
./manage-mailhog.sh start
```

## 📚 Recursos Adicionales

- [MailHog GitHub](https://github.com/mailhog/MailHog)
- [Docker Hub](https://hub.docker.com/r/mailhog/mailhog)
- [Documentación Oficial](https://github.com/mailhog/MailHog/blob/master/README.md)

## 🤝 Contribuir

Si encuentras algún problema o tienes sugerencias, por favor:
1. Revisa los logs: `./manage-mailhog.sh logs`
2. Verifica la configuración: `./manage-mailhog.sh check`
3. Reporta el problema con detalles del error
