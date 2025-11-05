from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing any modules
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .infrastructure.database import init_database
from .api.routes import (
    transactions_router,
    insights_router,
    catalogs_router,
    health_router,
    dashboard_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Flowlite Data Service",
    description="API for retrieving user transactions, insights, and catalog data",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(transactions_router)
app.include_router(insights_router)
app.include_router(catalogs_router)
app.include_router(health_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {
        "service": "Flowlite Data Service",
        "version": "1.0.0",
        "docs": "/docs",
    }
