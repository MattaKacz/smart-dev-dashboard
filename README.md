# Smart Dev Dashboard

AI-powered development dashboard for intelligent log analysis and debugging assistance.

## 🎯 Project Overview

Smart Dev Dashboard is an internal tool designed to help development teams analyze logs, identify issues, and get AI-powered suggestions for problem resolution. The system uses OpenAI's GPT-4 and FAISS vector search to provide contextual analysis of development logs and error messages.

## 🚀 Quick Start

```bash
# Run the application
docker-compose up app

# Run tests
docker-compose run --rm tests
```

## 📋 Project Context for AI Assistant

**IMPORTANT**: When working on this project, always refer to `PROJECT_SPEC.md` for complete context and requirements.

### Key Context Points:

- **MVP Focus**: AI log analysis + vector search (FAISS) + automated testing + CI/CD
- **Target Users**: Development teams (backend/devops), tech leads, QA
- **Scale**: Small team (2-5 users), scalable architecture
- **Tech Stack**: FastAPI, OpenAI GPT-4, FAISS, Docker, GitHub Actions
- **Priority**: Quick debugging assistance for developers

### Current Status:

- ✅ Basic FastAPI structure
- ✅ OpenAI integration
- ✅ Docker setup
- ✅ CI/CD pipeline
- 🔄 Vector search implementation (planned)
- 📋 Dashboard UI (future)

## 📖 Documentation

- **[PROJECT_SPEC.md](PROJECT_SPEC.md)** - Complete project specification and requirements
- API Documentation: Available at `/docs` when running the application

## 🔧 Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run tests
pytest
```

## 🐳 Docker

```bash
# Build and run
docker-compose up --build

# Run tests in container
docker-compose run --rm tests
```

---

**For AI Assistant**: Always check `PROJECT_SPEC.md` for detailed context before making changes or suggestions.
