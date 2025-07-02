from fastapi import APIRouter

router = APIRouter()

@router.get("/logs")
def get_logs():
    return {"message": "Logs endpoint"}
