"""
Smart Dev Dashboard - AI-powered log analysis tool

Project Context:
- MVP: AI log analysis + vector search (FAISS) + automated testing + CI/CD
- Target: Development teams (backend/devops), tech leads, QA
- Scale: Small team (2-5 users), scalable architecture
- Tech: FastAPI, OpenAI GPT-4, FAISS, Docker, GitHub Actions
- Priority: Quick debugging assistance for developers

See PROJECT_SPEC.md for complete requirements and context.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from app.api import logs, analyze, vector, metrics, logs_sql
from app.core.logger import logger
from app.core.middleware import LoggingMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from app.db import create_db_and_tables
from contextlib import asynccontextmanager




load_dotenv()

@asynccontextmanager
def lifespan(app: FastAPI):
    logger.info("Smart Dev Dashboard starting up...")
    create_db_and_tables()
    yield
    logger.info("Smart Dev Dashboard shutting down...")

app = FastAPI(
    title="Smart Dev Dashboard",
    description="AI-powered development dashboard for intelligent log analysis and debugging assistance",
    version="1.0.0",
    lifespan=lifespan
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(logs.router)
app.include_router(analyze.router)
app.include_router(vector.router)
app.include_router(metrics.router)
app.include_router(logs_sql.router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")



@app.get("/")
async def read_root():
    """Serve the main dashboard page"""
    return FileResponse("app/static/index.html")

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "timestamp": "2024-12-19T10:00:00Z"}