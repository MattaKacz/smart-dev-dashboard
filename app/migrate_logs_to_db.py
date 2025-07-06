import json
from pathlib import Path
from datetime import datetime
from sqlmodel import Session
from app.db import engine
from app.models.log_sql import LogFile, LogEntry

UPLOADS_DIR = Path("uploads")

def migrate():
    metadata_files = list(UPLOADS_DIR.glob("*_metadata.json"))
    print(f"Found {len(metadata_files)} metadata files.")

    with Session(engine) as session:
        for meta_path in metadata_files:
            with open(meta_path, "r") as f:
                data = json.load(f)

            # Stwórz LogFile
            log_file = LogFile(
                id=None,  # autoincrement
                filename=data["filename"],
                size=data["size"],
                upload_time=datetime.fromisoformat(data["upload_time"]),
                log_count=data["log_count"],
                log_analysis_status=data.get("log_analysis_status", "pending"),
                analysis_result=data.get("analysis_result")
            )
            session.add(log_file)
            session.commit()
            session.refresh(log_file)

            # Stwórz LogEntry dla każdego wpisu
            for entry in data.get("entries", []):
                log_entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    level=entry["level"],
                    message=entry["message"],
                    source=entry.get("source"),
                    log_metadata=json.dumps(entry.get("metadata", {}))  # zmień na log_metadata!
                )
                session.add(log_entry)
            session.commit()
            print(f"Migrated {log_file.filename} ({log_file.log_count} entries)")

if __name__ == "__main__":
    migrate()
    print("Migration complete!")