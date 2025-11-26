# ===========================================
# DOCKERFILE PARA INSIGHTSERVICE
# ===========================================

FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Flowlite Team - Carlos Felipe Caro Arroyave & Joiver Andrés Gómez Coronado"
LABEL description="Insight Service - Microservicio de generación de insights financieros con IA"
LABEL version="1.0.0"

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY ../../InsightService/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY ../../InsightService/src/ src/
COPY ../../InsightService/main.py .

# Crear usuario no-root para seguridad
RUN groupadd -g 1001 flowlite && \
    useradd -u 1001 -g flowlite -m -s /bin/bash flowlite && \
    chown -R flowlite:flowlite /app

# Cambiar al usuario no-root
USER flowlite

# Exponer puerto para API
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Comando para ejecutar el servicio (API + RabbitMQ consumer)
CMD ["python", "main.py"]
