"""
FastAPI application for InsightService Health Checks
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str = "InsightService"
    version: str = "1.0.0"


class DatabaseCheckResponse(BaseModel):
    """Database check response model"""
    status: str
    database: str
    connected: bool
    timestamp: str
    message: Optional[str] = None


def create_app(container) -> FastAPI:
    """
    Create and configure FastAPI application

    Args:
        container: Dependency injection container with settings and database
    """
    app = FastAPI(
        title="InsightService API",
        description="Financial Insights Service - Health Check and Monitoring",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for local development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_model=HealthResponse)
    async def root():
        """Root endpoint"""
        return HealthResponse(
            status="ok",
            timestamp=datetime.utcnow().isoformat()
        )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Basic health check endpoint

        Returns:
            HealthResponse: Service status and metadata
        """
        logger.info("Health check requested")
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat()
        )

    @app.get("/health/db", response_model=DatabaseCheckResponse)
    async def database_check():
        """
        Database health check endpoint

        Verifies connection to MySQL database

        Returns:
            DatabaseCheckResponse: Database connection status
        """
        logger.info("Database health check requested")

        try:
            # Get database session from container
            session = container.database_session

            # Test database connection with a simple query
            result = session.execute(text("SELECT 1"))
            result.fetchone()

            logger.info("Database check successful")
            return DatabaseCheckResponse(
                status="healthy",
                database="MySQL",
                connected=True,
                timestamp=datetime.utcnow().isoformat(),
                message="Database connection successful"
            )

        except Exception as e:
            logger.error(f"Database check failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=DatabaseCheckResponse(
                    status="unhealthy",
                    database="MySQL",
                    connected=False,
                    timestamp=datetime.utcnow().isoformat(),
                    message=f"Database connection failed: {str(e)}"
                ).dict()
            )

    @app.get("/health/full")
    async def full_health_check():
        """
        Complete health check including all dependencies

        Returns:
            dict: Detailed health status of all components
        """
        logger.info("Full health check requested")

        health_status = {
            "service": "InsightService",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }

        # Check database
        try:
            session = container.database_session
            session.execute(text("SELECT 1"))
            health_status["components"]["database"] = {
                "status": "healthy",
                "type": "MySQL"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "type": "MySQL",
                "error": str(e)
            }
            health_status["status"] = "degraded"

        # Check RabbitMQ (basic check if consumer is configured)
        try:
            rabbitmq_consumer = container.rabbitmq_consumer
            if rabbitmq_consumer:
                health_status["components"]["rabbitmq"] = {
                    "status": "configured",
                    "queue": container.settings.rabbitmq_queue
                }
            else:
                health_status["components"]["rabbitmq"] = {
                    "status": "not_configured"
                }
        except Exception as e:
            health_status["components"]["rabbitmq"] = {
                "status": "error",
                "error": str(e)
            }

        # Check LLM configuration
        try:
            settings = container.settings
            health_status["components"]["llm"] = {
                "status": "configured",
                "host": settings.ollama_host,
                "model": settings.llm_model
            }
        except Exception as e:
            health_status["components"]["llm"] = {
                "status": "error",
                "error": str(e)
            }

        # Determine overall status based on components
        component_statuses = [
            comp.get("status") for comp in health_status["components"].values()
        ]

        if "unhealthy" in component_statuses:
            health_status["status"] = "unhealthy"
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
        elif "degraded" in component_statuses or "error" in component_statuses:
            health_status["status"] = "degraded"
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health_status
            )

        return health_status

    @app.get("/info")
    async def service_info():
        """
        Service information endpoint

        Returns:
            dict: Service configuration and metadata
        """
        settings = container.settings
        return {
            "service": "InsightService",
            "version": "1.0.0",
            "description": "Financial Insights Service with AI-powered analysis",
            "config": {
                "database": settings.database_url.split('@')[-1],  # Hide credentials
                "rabbitmq": {
                    "host": settings.rabbitmq_host,
                    "port": settings.rabbitmq_port,
                    "queue": settings.rabbitmq_queue
                },
                "llm": {
                    "model": settings.llm_model,
                    "temperature": settings.llm_temperature
                },
                "api": {
                    "host": settings.api_host,
                    "port": settings.api_port
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    return app
