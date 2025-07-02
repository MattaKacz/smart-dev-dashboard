from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gpt_service import analyze_logs

router = APIRouter()

class LogRequest(BaseModel):
    log: str

@router.post("/analyze")
async def analyze_log(request: LogRequest):
    if not request.log.strip():
        raise HTTPException(status_code=400, detail="Log cannot be empty.")
    
    try:
        result = analyze_logs(request.log)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
