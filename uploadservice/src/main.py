from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing any modules
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .infrastructure.database import init_database
from .api.routes import transactions_router, health_router, test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Bank Transaction Service",
    description="API for processing and classifying bank transactions from Excel files",
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
app.include_router(health_router)
app.include_router(test_router)


@app.get("/")
async def root():
    return {
        "service": "Bank Transaction Service",
        "version": "1.0.0",
        "docs": "/docs",
    }
