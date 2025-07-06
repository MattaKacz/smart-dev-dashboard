import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.models.log import LogUploadResponse, LogListResponse
from app.services.log_manager import LogManager
from app.core.logger import logger

router = APIRouter()

# Initialize log manager
log_manager = LogManager()

@router.get("/logs", response_model=LogListResponse)
async def get_logs():
    """Get all uploaded log files"""
    try:
        return log_manager.get_all_files()
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

@router.post("/logs/upload", response_model=LogUploadResponse)
async def upload_log_file(file: UploadFile = File(...)):
    """Upload a log file for analysis"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.log', '.txt')):
            raise HTTPException(status_code=400, detail="Only .log and .txt files are supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as temp_file:
            # Write uploaded content to temp file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # Upload and parse the file
            log_file = log_manager.upload_file(temp_file_path, file.filename)
            
            return LogUploadResponse(
                file_id=log_file.id,
                filename=log_file.filename,
                size=log_file.size,
                log_count=log_file.log_count,
                message=f"Successfully uploaded {file.filename} with {log_file.log_count} log entries"
            )
            
        finally:
            # Clean up temp file
            temp_file_path.unlink(missing_ok=True)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/logs/{file_id}")
async def get_log_file(file_id: str):
    """Get specific log file details"""
    try:
        log_file = log_manager.get_file(file_id)
        if not log_file:
            raise HTTPException(status_code=404, detail="Log file not found")
        
        return log_file
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting log file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve log file")

@router.post("/logs/{file_id}/analyze")
async def analyze_log_file(file_id: str):
    """Analyze a log file using AI"""
    try:
        analysis_result = log_manager.analyze_file(file_id)
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Log file not found")
        
        return {
            "file_id": file_id,
            "analysis": analysis_result,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {str(e)}")

@router.delete("/logs/{file_id}")
async def delete_log_file(file_id: str):
    """Delete a log file"""
    try:
        success = log_manager.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=404, detail="Log file not found")
        
        return {"message": "Log file deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/logs/{file_id}/download")
async def download_log_file(file_id: str):
    """Download the original log file"""
    try:
        log_file = log_manager.get_file(file_id)
        if not log_file:
            raise HTTPException(status_code=404, detail="Log file not found")
        
        file_path = log_manager.storage_dir / f"{file_id}_{log_file.filename}"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            filename=log_file.filename,
            media_type='text/plain'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")
