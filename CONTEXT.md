# AI Assistant Context - Smart Dev Dashboard

## 🎯 Quick Reference for AI Assistant

**ALWAYS READ THIS BEFORE MAKING CHANGES OR SUGGESTIONS**

### Project Identity

- **Name**: Smart Dev Dashboard
- **Purpose**: AI-powered log analysis and debugging assistance
- **Type**: Internal development tool
- **Scale**: Small team (2-5 users), scalable architecture

### MVP Priorities (Current Focus)

1. **AI Log Analysis** - GPT-4 powered analysis with error summaries
2. **Vector Search (FAISS)** - Fast similarity search for similar incidents
3. **Automated Testing** - Comprehensive Pytest suite
4. **CI/CD Pipeline** - GitHub Actions + Docker automation

### Target Users

- **Primary**: Development teams (backend/devops)
- **Secondary**: Tech leads, QA teams
- **Use Case**: Quick debugging assistance during incident response

### Tech Stack

- **Backend**: FastAPI (Python 3.13)
- **AI**: OpenAI GPT-4 API
- **Search**: FAISS vector similarity
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest + httpx

### Current Status

- ✅ Basic FastAPI structure
- ✅ OpenAI integration
- ✅ Docker setup
- ✅ CI/CD pipeline
- 🔄 Vector search implementation (planned)
- 📋 Dashboard UI (future)

### Key Constraints

- **Language**: Polish (primary), English (fallback)
- **Deployment**: Local server, Azure, or VPS
- **Security**: Internal tool, no public access needed
- **Performance**: Fast response times for debugging scenarios

### Development Guidelines

- Follow PEP 8 standards
- Use type hints
- Comprehensive testing
- Clear error messages
- Modular architecture

### Important Files

- `PROJECT_SPEC.md` - Complete project specification
- `app/main.py` - FastAPI application entry point
- `app/services/gpt_service.py` - OpenAI integration
- `app/api/analyze.py` - Log analysis endpoint
- `requirements.txt` - Dependencies

### Next Steps (MVP)

1. Implement FAISS vector search service
2. Add log file upload functionality
3. Enhance error handling and validation
4. Improve test coverage
5. Add structured logging

---

**Remember**: This is an MVP focused on providing quick, AI-powered debugging assistance to development teams. Keep it simple, fast, and practical.
