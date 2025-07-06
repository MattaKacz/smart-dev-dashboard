"""
Log management service for storing and analyzing log files
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from app.models.log import LogFile, LogListResponse
from app.services.log_parser import LogParser
from app.services.mock_gpt_service import analyze_logs
from app.services.vector_singleton import vector_service
from app.core.logger import logger

class LogManager:
    """Manages log file storage and analysis"""
    
    def __init__(self, storage_dir: str = "uploads"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.parser = LogParser()
        self.log_files: dict[str, LogFile] = {}
        
        # Load existing log files
        self._load_existing_files()
    
    def upload_file(self, file_path: Path, filename: str) -> LogFile:
        """Upload and parse a log file"""
        try:
            logger.info(f"Uploading log file: {filename}")
            
            # Parse the log file
            log_file = self.parser.parse_log_file(file_path, filename)
            
            # Save file to storage
            storage_path = self.storage_dir / f"{log_file.id}_{filename}"
            shutil.copy2(file_path, storage_path)
            
            # Save metadata
            self._save_metadata(log_file)
            
            # Add to memory cache
            self.log_files[log_file.id] = log_file
            
            logger.info(f"Successfully uploaded {filename} with {log_file.log_count} entries")
            return log_file
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {str(e)}")
            raise
    
    def get_all_files(self) -> LogListResponse:
        """Get all uploaded log files"""
        files = list(self.log_files.values())
        total_size = sum(f.size for f in files)
        
        return LogListResponse(
            files=files,
            total_count=len(files),
            total_size=total_size
        )
    
    def get_file(self, file_id: str) -> Optional[LogFile]:
        """Get a specific log file by ID"""
        return self.log_files.get(file_id)
    
    def analyze_file(self, file_id: str) -> Optional[str]:
        """Analyze a log file using AI"""
        try:
            log_file = self.get_file(file_id)
            if not log_file:
                logger.warning(f"Log file not found: {file_id}")
                return None
            
            logger.info(f"Starting AI analysis for file: {log_file.filename}")
            
            # Combine all log entries into a single text
            log_content = self._combine_log_entries(log_file.entries)
            
            # Analyze with AI
            analysis_result = analyze_logs(log_content)
            
            # Update log file with analysis result
            log_file.log_analysis_status = "completed"
            log_file.analysis_result = analysis_result
            
            # Add to vector database for similarity search
            self._add_to_vector_db(log_file, log_content)
            
            # Save updated metadata
            self._save_metadata(log_file)
            
            logger.info(f"AI analysis completed for {log_file.filename}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_id}: {str(e)}")
            raise
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a log file"""
        try:
            log_file = self.get_file(file_id)
            if not log_file:
                return False
            
            # Remove from storage
            storage_path = self.storage_dir / f"{file_id}_{log_file.filename}"
            if storage_path.exists():
                storage_path.unlink()
            
            # Remove metadata file
            metadata_path = self.storage_dir / f"{file_id}_metadata.json"
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Remove from memory cache
            del self.log_files[file_id]
            
            logger.info(f"Deleted log file: {log_file.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return False
    
    def _combine_log_entries(self, entries: List) -> str:
        """Combine log entries into a single text for analysis"""
        lines = []
        for entry in entries:
            timestamp = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"{timestamp} {entry.level} {entry.message}")
        
        return "\n".join(lines)
    
    def _save_metadata(self, log_file: LogFile):
        """Save log file metadata to disk"""
        metadata_path = self.storage_dir / f"{log_file.id}_metadata.json"
        
        # Convert to dict for JSON serialization
        metadata = {
            'id': log_file.id,
            'filename': log_file.filename,
            'size': log_file.size,
            'upload_time': log_file.upload_time.isoformat(),
            'log_count': log_file.log_count,
            'log_analysis_status': log_file.log_analysis_status,
            'analysis_result': log_file.analysis_result,
            'entries': [
                {
                    'id': entry.id,
                    'timestamp': entry.timestamp.isoformat(),
                    'level': entry.level,
                    'message': entry.message,
                    'source': entry.source,
                    'metadata': entry.metadata
                }
                for entry in log_file.entries
            ]
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_existing_files(self):
        """Load existing log files from disk"""
        try:
            for metadata_file in self.storage_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                    
                    # Reconstruct LogFile object
                    log_file = LogFile(
                        id=data['id'],
                        filename=data['filename'],
                        size=data['size'],
                        upload_time=datetime.fromisoformat(data['upload_time']),
                        log_count=data['log_count'],
                        log_analysis_status=data['log_analysis_status'],
                        analysis_result=data['analysis_result'],
                        entries=[]  # We'll load entries if needed
                    )
                    
                    self.log_files[log_file.id] = log_file
                    
                except Exception as e:
                    logger.warning(f"Error loading metadata file {metadata_file}: {str(e)}")
                    continue
            
            logger.info(f"Loaded {len(self.log_files)} existing log files")
            
        except Exception as e:
            logger.error(f"Error loading existing files: {str(e)}")
    
    def _add_to_vector_db(self, log_file: LogFile, log_content: str):
        """Add analyzed log to vector database"""
        try:
            # Determine severity and category based on log content
            severity = self._determine_severity(log_content)
            category = self._determine_category(log_content)
            
            # Add to vector database
            incident_id = vector_service.add_incident(
                log_content=log_content,
                analysis=log_file.analysis_result,
                source_file=log_file.filename,
                severity=severity,
                category=category
            )
            
            logger.info(f"Added incident {incident_id} to vector database")
            
        except Exception as e:
            logger.error(f"Error adding to vector database: {str(e)}")
    
    def _determine_severity(self, log_content: str) -> str:
        """Determine incident severity based on log content"""
        content_lower = log_content.lower()
        
        if any(word in content_lower for word in ['fatal', 'critical', 'emergency']):
            return 'critical'
        elif any(word in content_lower for word in ['error', 'failed', 'exception']):
            return 'high'
        elif any(word in content_lower for word in ['warning', 'timeout']):
            return 'medium'
        else:
            return 'low'
    
    def _determine_category(self, log_content: str) -> str:
        """Determine incident category based on log content"""
        content_lower = log_content.lower()
        
        if any(word in content_lower for word in ['database', 'db', 'sql', 'postgresql', 'mysql']):
            return 'database'
        elif any(word in content_lower for word in ['memory', 'heap', 'out of memory']):
            return 'memory'
        elif any(word in content_lower for word in ['network', 'connection', 'timeout', 'dns']):
            return 'network'
        elif any(word in content_lower for word in ['disk', 'storage', 'space']):
            return 'storage'
        elif any(word in content_lower for word in ['security', 'auth', 'permission']):
            return 'security'
        else:
            return 'general' 