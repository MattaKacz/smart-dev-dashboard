"""
Data models for log management
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class LogEntry(BaseModel):
    """Single log entry"""
    id: str = Field(description="Unique identifier")
    timestamp: datetime = Field(description="Log timestamp")
    level: str = Field(description="Log level (INFO, ERROR, WARNING, etc.)")
    message: str = Field(description="Log message")
    source: str = Field(description="Source of the log")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")

class LogFile(BaseModel):
    """Log file information"""
    id: str = Field(description="Unique file identifier")
    filename: str = Field(description="Original filename")
    size: int = Field(description="File size in bytes")
    upload_time: datetime = Field(description="Upload timestamp")
    log_count: int = Field(description="Number of log entries")
    log_analysis_status: str = Field(default="pending", description="Analysis status")
    analysis_result: Optional[str] = Field(default=None, description="Analysis result")
    entries: List[LogEntry] = Field(default=[], description="Parsed log entries")

class LogUploadResponse(BaseModel):
    """Response for log upload"""
    file_id: str = Field(description="Uploaded file ID")
    filename: str = Field(description="Original filename")
    size: int = Field(description="File size in bytes")
    log_count: int = Field(description="Number of parsed log entries")
    message: str = Field(description="Upload status message")

class LogListResponse(BaseModel):
    """Response for log list"""
    files: List[LogFile] = Field(description="List of uploaded log files")
    total_count: int = Field(description="Total number of files")
    total_size: int = Field(description="Total size of all files") 