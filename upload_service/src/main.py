from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .infrastructure.database import init_database
from .api.routes import transacciones_router, health_router, test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Servicio de Transacciones Bancarias",
    description="API para procesar y clasificar transacciones bancarias desde archivos Excel",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(transacciones_router)
app.include_router(health_router)
app.include_router(test_router)


@app.get("/")
async def root():
    return {
        "service": "Servicio de Transacciones Bancarias",
        "version": "1.0.0",
        "docs": "/docs",
    }
