#!/usr/bin/env python3
"""
Script to create log entries from existing log files in the database
"""

import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Optional

def parse_log_line(line: str, log_file_id: int) -> Optional[Dict]:
    """Parse a log line and return a log entry dictionary"""
    if not line.strip():
        return None
    
    try:
        # Default values
        timestamp = datetime.now().isoformat()
        level = 'INFO'
        message = line.strip()
        source = 'unknown'
        log_metadata = None
        
        # Try to extract timestamp
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)'
        timestamp_match = re.search(timestamp_pattern, line)
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            message = line.replace(timestamp_match.group(0), '').strip()
        
        # Try to extract log level
        level_patterns = [
            r'\[(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG)\]',
            r'(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG):',
            r'\b(CRITICAL|ERROR|WARN|WARNING|INFO|DEBUG)\b'
        ]
        
        for pattern in level_patterns:
            level_match = re.search(pattern, message, re.IGNORECASE)
            if level_match:
                level = level_match.group(1).upper()
                message = re.sub(pattern, '', message, flags=re.IGNORECASE).strip()
                break
        
        # Try to extract source/component
        source_pattern = r'\[([^\]]+)\]'
        source_match = re.search(source_pattern, message)
        if source_match:
            source = source_match.group(1)
            message = re.sub(source_pattern, '', message).strip()
        
        # Clean up message
        message = re.sub(r'^\s*[-:]\s*', '', message).strip()
        
        return {
            'log_file_id': log_file_id,
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'source': source,
            'log_metadata': log_metadata
        }
    except Exception as e:
        print(f"Error parsing line: {line} - {e}")
        return None

def create_log_entries():
    """Create log entries from existing log files"""
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    
    try:
        # Get all log files
        cursor.execute("SELECT id, filename, content FROM logfile")
        log_files = cursor.fetchall()
        
        print(f"Found {len(log_files)} log files to process")
        
        for log_file_id, filename, content in log_files:
            if not content:
                print(f"Skipping {filename} - no content")
                continue
            
            print(f"Processing {filename} (ID: {log_file_id})")
            
            # Split content into lines
            lines = content.split('\n')
            entries_created = 0
            
            for line in lines:
                if line.strip():
                    log_entry = parse_log_line(line, log_file_id)
                    if log_entry:
                        # Insert log entry
                        cursor.execute("""
                            INSERT INTO logentry (log_file_id, timestamp, level, message, source, log_metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            log_entry['log_file_id'],
                            log_entry['timestamp'],
                            log_entry['level'],
                            log_entry['message'],
                            log_entry['source'],
                            log_entry['log_metadata']
                        ))
                        entries_created += 1
            
            # Update log_count in logfile
            cursor.execute("UPDATE logfile SET log_count = ? WHERE id = ?", (entries_created, log_file_id))
            print(f"Created {entries_created} log entries for {filename}")
        
        # Commit changes
        conn.commit()
        print("Successfully created log entries!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM logentry")
        total_entries = cursor.fetchone()[0]
        print(f"Total log entries in database: {total_entries}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_log_entries() 