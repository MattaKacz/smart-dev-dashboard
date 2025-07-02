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
from dotenv import load_dotenv
from app.api import logs, analyze
import os

load_dotenv()

app = FastAPI(
    title="Smart Dev Dashboard",
    description="AI-powered development dashboard for intelligent log analysis and debugging assistance",
    version="1.0.0"
)
app.include_router(logs.router)
app.include_router(analyze.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}