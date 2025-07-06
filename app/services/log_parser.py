"""
Log parsing service for different log formats
"""
import re
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from app.models.log import LogEntry, LogFile
from app.core.logger import logger

class LogParser:
    """Parser for different log formats"""
    
    def __init__(self):
        # Common log patterns
        self.patterns = {
            'custom': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] ([^:]+):([^:]+):(\d+) - (.+)'),
            'iso_error': re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) \[(\w+)\] (.+)'),
            'standard': re.compile(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\w+)\s+(.+)'),
            'nginx': re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)'),
            'apache': re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)'),
            'docker': re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\w+)\s+(.+)'),
            'kubernetes': re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\w+)\s+(\w+)\s+(.+)'),
        }
    
    def parse_log_file(self, file_path: Path, filename: str) -> LogFile:
        """Parse a log file and return LogFile object"""
        try:
            logger.info(f"Parsing log file: {filename}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse log entries
            entries = self._parse_content(content, filename)
            
            # Create LogFile object
            log_file = LogFile(
                id=str(uuid.uuid4()),
                filename=filename,
                size=len(content),
                upload_time=datetime.utcnow(),
                log_count=len(entries),
                entries=entries
            )
            
            logger.info(f"Successfully parsed {len(entries)} log entries from {filename}")
            return log_file
            
        except Exception as e:
            logger.error(f"Error parsing log file {filename}: {str(e)}")
            raise
    
    def _parse_content(self, content: str, filename: str) -> List[LogEntry]:
        """Parse log content into LogEntry objects (strict multi-line: 'custom' or 'iso_error' pattern starts new entry)"""
        entries = []
        lines = content.split('\n')
        current_entry = None
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            match_custom = self.patterns['custom'].match(line.strip())
            match_iso = self.patterns['iso_error'].match(line.strip())
            if match_custom:
                if current_entry:
                    entries.append(current_entry)
                current_entry = self._create_entry_from_match(match_custom, 'custom', filename, line_num, line)
            elif match_iso:
                if current_entry:
                    entries.append(current_entry)
                # Tworzymy LogEntry dla iso_error
                timestamp_str, level, message = match_iso.groups()
                timestamp = self._parse_timestamp(timestamp_str)
                current_entry = LogEntry(
                    id=str(uuid.uuid4()),
                    timestamp=timestamp,
                    level=level.upper(),
                    message=message,
                    source=filename,
                    metadata={
                        'pattern': 'iso_error',
                        'line_number': line_num,
                        'original_line': line
                    }
                )
            else:
                if current_entry:
                    current_entry.message += '\n' + line
                else:
                    continue
        if current_entry:
            entries.append(current_entry)
        return entries
    
    def _parse_line(self, line: str, source: str, line_num: int) -> Optional[LogEntry]:
        """Parse a single log line"""
        try:
            # Try different patterns
            for pattern_name, pattern in self.patterns.items():
                match = pattern.match(line.strip())
                if match:
                    return self._create_entry_from_match(match, pattern_name, source, line_num, line)
            
            # If no pattern matches, create a generic entry
            return self._create_generic_entry(line, source, line_num)
            
        except Exception as e:
            logger.warning(f"Error parsing line {line_num}: {str(e)}")
            return None
    
    def _create_entry_from_match(self, match, pattern_name: str, source: str, line_num: int, original_line: str) -> LogEntry:
        """Create LogEntry from regex match"""
        groups = match.groups()
        
        if pattern_name == 'custom':
            timestamp_str, level, log_source, function, line_number, message = groups
            timestamp = self._parse_timestamp(timestamp_str)
            return LogEntry(
                id=str(uuid.uuid4()),
                timestamp=timestamp,
                level=level.upper(),
                message=message,
                source=log_source,
                metadata={
                    'pattern': pattern_name,
                    'function_name': function,
                    'line_number': int(line_number),
                    'line': line_num,
                    'original_line': original_line
                }
            )
        elif pattern_name == 'standard':
            timestamp_str, level, message = groups
            timestamp = self._parse_timestamp(timestamp_str)
            
        elif pattern_name in ['nginx', 'apache']:
            ip, timestamp_str, request, status, size = groups
            timestamp = self._parse_timestamp(timestamp_str)
            level = 'INFO' if int(status) < 400 else 'ERROR'
            message = f"{request} - {status} - {size} bytes"
            
        elif pattern_name == 'docker':
            timestamp_str, level, message = groups
            timestamp = self._parse_timestamp(timestamp_str)
            
        elif pattern_name == 'kubernetes':
            timestamp_str, level, pod, message = groups
            timestamp = self._parse_timestamp(timestamp_str)
            message = f"[{pod}] {message}"
            
        else:
            # Fallback
            timestamp = datetime.utcnow()
            level = 'INFO'
            message = original_line
        
        return LogEntry(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            level=level.upper(),
            message=message,
            source=source,
            metadata={
                'pattern': pattern_name,
                'line_number': line_num,
                'original_line': original_line
            }
        )
    
    def _create_generic_entry(self, line: str, source: str, line_num: int) -> LogEntry:
        """Create generic LogEntry for unmatched lines"""
        # Try to extract timestamp and level from the beginning
        parts = line.split(' ', 2)
        
        if len(parts) >= 3:
            timestamp_str, level, message = parts
            timestamp = self._parse_timestamp(timestamp_str) or datetime.utcnow()
        else:
            timestamp = datetime.utcnow()
            level = 'INFO'
            message = line
        
        return LogEntry(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            level=level.upper(),
            message=message,
            source=source,
            metadata={
                'pattern': 'generic',
                'line_number': line_num,
                'original_line': line
            }
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        try:
            # Remove timezone info for parsing
            clean_timestamp = re.sub(r'[+-]\d{2}:\d{2}$', '', timestamp_str)
            clean_timestamp = clean_timestamp.replace('Z', '')
            
            # Try different formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%d/%b/%Y:%H:%M:%S %z',
                '%d/%b/%Y:%H:%M:%S',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(clean_timestamp, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None 