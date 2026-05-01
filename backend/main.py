"""
Verity — Autonomous Research & Decision Engine
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from routes.auth import router as auth_router
from routes.queries import router as queries_router
from routes.reports import router as reports_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — create tables on startup."""
    logger.info("🚀 Verity API starting up...")
    await create_tables()
    logger.info("✅ Database tables created/verified")
    yield
    logger.info("🛑 Verity API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Verity — Autonomous Research & Decision Engine",
    description="AI-powered multi-step research system that decomposes queries, researches sub-questions, and synthesizes structured reports.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware — allow React dev server and Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite React dev server
        "http://localhost:3000",   # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://10.0.2.2:8000",   # Android emulator
        "*",                       # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(queries_router)
app.include_router(reports_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "Verity API",
        "status": "operational",
        "version": "1.0.0",
    }
