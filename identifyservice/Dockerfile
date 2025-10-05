# ===========================================
# DOCKERFILE MULTI-STAGE PARA IDENTIFYSERVICE
# ===========================================

# Etapa 1: Construcción
FROM eclipse-temurin:17-jdk AS builder

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de Gradle
COPY gradle/ gradle/
COPY gradlew .
COPY gradlew.bat .
COPY build.gradle .
COPY settings.gradle .

# Hacer ejecutable el wrapper de Gradle
RUN chmod +x gradlew

# Copiar código fuente
COPY src/ src/

# Construir la aplicación (con reintentos y configuración de red)
RUN ./gradlew clean build -x test --no-daemon --stacktrace --info --refresh-dependencies

# Etapa 2: Runtime
FROM eclipse-temurin:17-jre

# Metadatos del contenedor
LABEL maintainer="Flowlite Team"
LABEL description="Identify Service - Microservicio de autenticación y autorización"
LABEL version="0.0.1-SNAPSHOT"

# Crear usuario no-root para seguridad
RUN groupadd -g 1001 flowlite && \
    useradd -u 1001 -g flowlite -m -s /bin/bash flowlite

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configurar zona horaria
ENV TZ=America/Bogota
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiar el JAR construido desde la etapa anterior
COPY --from=builder /app/build/libs/identifyservice-0.0.1-SNAPSHOT.jar app.jar

# Crear directorio para logs
RUN mkdir -p /app/logs && chown -R flowlite:flowlite /app

# Cambiar al usuario no-root
USER flowlite

# Exponer puerto de la aplicación
EXPOSE 8080

# Variables de entorno por defecto
ENV SPRING_PROFILES_ACTIVE=docker
ENV SERVER_PORT=8080
ENV JWT_SECRET=mi_clave_super_secreta_de_32_caracteres_minimo_123456789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Comando para ejecutar la aplicación
CMD ["java", "-jar", "app.jar"]
