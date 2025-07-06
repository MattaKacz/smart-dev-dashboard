from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.log_sql import LogFile, LogEntry
from datetime import datetime
from typing import List
import json
from app.services.log_parser import LogParser

router = APIRouter()

# LogFile CRUD
@router.post("/logs_sql", response_model=LogFile)
def create_log_file(log_file: LogFile, session: Session = Depends(get_session)):
    # Ensure upload_time is a datetime object
    if isinstance(log_file.upload_time, str):
        log_file.upload_time = datetime.fromisoformat(log_file.upload_time)
    session.add(log_file)
    session.commit()
    session.refresh(log_file)

    # --- AUTOMATYCZNE PARSOWANIE LOGÓW NA WPISY ---
    if log_file.content:
        parser = LogParser()
        entries = parser._parse_content(log_file.content, log_file.filename)
        log_entries = []
        for entry in entries:
            # Tworzymy LogEntry zgodny z modelem SQLModel
            log_entry = LogEntry(
                log_file_id=log_file.id,
                timestamp=entry.timestamp,
                level=entry.level,
                message=entry.message,
                source=entry.source,
                log_metadata=json.dumps(getattr(entry, 'metadata', {})) if hasattr(entry, 'metadata') else None
            )
            session.add(log_entry)
            log_entries.append(log_entry)
        session.commit()
        # Zaktualizuj log_count
        log_file.log_count = len(log_entries)
        session.add(log_file)
        session.commit()
        session.refresh(log_file)
    return log_file

@router.get("/logs_sql", response_model=List[LogFile])
def read_log_files(session: Session = Depends(get_session)):
    return session.exec(select(LogFile)).all()

@router.get("/logs_sql/{log_file_id}", response_model=LogFile)
def read_log_file(log_file_id: int, session: Session = Depends(get_session)):
    log_file = session.get(LogFile, log_file_id)
    if not log_file:
        raise HTTPException(status_code=404, detail="LogFile not found")
    return log_file

@router.put("/logs_sql/{log_file_id}", response_model=LogFile)
def update_log_file(log_file_id: int, log_file: LogFile, session: Session = Depends(get_session)):
    db_log_file = session.get(LogFile, log_file_id)
    if not db_log_file:
        raise HTTPException(status_code=404, detail="LogFile not found")
    log_file.id = log_file_id
    if isinstance(log_file.upload_time, str):
        log_file.upload_time = datetime.fromisoformat(log_file.upload_time)
    session.merge(log_file)
    session.commit()
    return log_file

@router.delete("/logs_sql/{log_file_id}")
def delete_log_file(log_file_id: int, session: Session = Depends(get_session)):
    log_file = session.get(LogFile, log_file_id)
    if not log_file:
        raise HTTPException(status_code=404, detail="LogFile not found")
    session.delete(log_file)
    session.commit()
    return {"ok": True}

# LogEntry CRUD
@router.post("/log_entries_sql", response_model=LogEntry)
def create_log_entry(log_entry: LogEntry, session: Session = Depends(get_session)):
    session.add(log_entry)
    session.commit()
    session.refresh(log_entry)
    return log_entry

@router.get("/log_entries_sql", response_model=List[LogEntry])
def read_log_entries(session: Session = Depends(get_session)):
    return session.exec(select(LogEntry)).all()

@router.get("/log_entries_sql/{log_entry_id}", response_model=LogEntry)
def read_log_entry(log_entry_id: int, session: Session = Depends(get_session)):
    log_entry = session.get(LogEntry, log_entry_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="LogEntry not found")
    return log_entry

@router.put("/log_entries_sql/{log_entry_id}", response_model=LogEntry)
def update_log_entry(log_entry_id: int, log_entry: LogEntry, session: Session = Depends(get_session)):
    db_log_entry = session.get(LogEntry, log_entry_id)
    if not db_log_entry:
        raise HTTPException(status_code=404, detail="LogEntry not found")
    log_entry.id = log_entry_id
    session.merge(log_entry)
    session.commit()
    return log_entry

@router.delete("/log_entries_sql/{log_entry_id}")
def delete_log_entry(log_entry_id: int, session: Session = Depends(get_session)):
    log_entry = session.get(LogEntry, log_entry_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="LogEntry not found")
    session.delete(log_entry)
    session.commit()
    return {"ok": True} 