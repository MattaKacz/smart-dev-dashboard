from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class LogEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    log_file_id: Optional[int] = Field(default=None, foreign_key="logfile.id")
    timestamp: datetime
    level: str
    message: str
    source: Optional[str] = None
    log_metadata: Optional[str] = None  # zamiast metadata

    log_file: Optional["LogFile"] = Relationship(back_populates="entries")

class LogFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    size: int
    upload_time: datetime
    log_count: int
    log_analysis_status: str = "pending"
    analysis_result: Optional[str] = None
    content: Optional[str] = None  # <-- to pole!

    entries: List[LogEntry] = Relationship(back_populates="log_file") 