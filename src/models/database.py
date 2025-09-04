"""
Database manager for SQLite operations.
"""

import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

from .schemas import FormMetadata, ExtractedData, ExtractionConfig

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: str = "data/pdf_extractor.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_tables()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create forms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    upload_date TIMESTAMP NOT NULL,
                    form_type TEXT NOT NULL,
                    processing_status TEXT NOT NULL DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create extracted_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extracted_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    field_value TEXT NOT NULL,
                    confidence_score REAL,
                    extraction_date TIMESTAMP NOT NULL,
                    raw_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms (id)
                )
            """)
            
            # Create form_templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS form_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    extraction_fields TEXT NOT NULL,
                    example_prompt TEXT,
                    validation_rules TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    def insert_form(self, form: FormMetadata) -> int:
        """Insert a new form record and return the ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO forms (filename, file_size, upload_date, form_type, processing_status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                form.filename,
                form.file_size,
                form.upload_date.isoformat(),
                form.form_type,
                form.processing_status,
                form.error_message
            ))
            form_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Inserted form with ID: {form_id}")
            return form_id
    
    def update_form_status(self, form_id: int, status: str, error_message: Optional[str] = None):
        """Update form processing status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE forms 
                SET processing_status = ?, error_message = ?
                WHERE id = ?
            """, (status, error_message, form_id))
            conn.commit()
            logger.info(f"Updated form {form_id} status to: {status}")
    
    def insert_extracted_data(self, data_list: List[ExtractedData]):
        """Insert multiple extracted data records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for data in data_list:
                cursor.execute("""
                    INSERT INTO extracted_data (form_id, field_name, field_value, confidence_score, extraction_date, raw_text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.form_id,
                    data.field_name,
                    data.field_value,
                    data.confidence_score,
                    data.extraction_date.isoformat(),
                    data.raw_text
                ))
            conn.commit()
            logger.info(f"Inserted {len(data_list)} extracted data records")
    
    def get_form_by_id(self, form_id: int) -> Optional[FormMetadata]:
        """Get form metadata by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM forms WHERE id = ?", (form_id,))
            row = cursor.fetchone()
            
            if row:
                return FormMetadata(
                    id=row[0],
                    filename=row[1],
                    file_size=row[2],
                    upload_date=datetime.fromisoformat(row[3]),
                    form_type=row[4],
                    processing_status=row[5],
                    error_message=row[6]
                )
            return None
    
    def get_extracted_data_by_form_id(self, form_id: int) -> List[ExtractedData]:
        """Get all extracted data for a specific form."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM extracted_data WHERE form_id = ?", (form_id,))
            rows = cursor.fetchall()
            
            return [
                ExtractedData(
                    id=row[0],
                    form_id=row[1],
                    field_name=row[2],
                    field_value=row[3],
                    confidence_score=row[4],
                    extraction_date=datetime.fromisoformat(row[5]),
                    raw_text=row[6]
                )
                for row in rows
            ]
    
    def get_all_forms(self, limit: int = 100) -> List[FormMetadata]:
        """Get all forms with optional limit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM forms ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            return [
                FormMetadata(
                    id=row[0],
                    filename=row[1],
                    file_size=row[2],
                    upload_date=datetime.fromisoformat(row[3]),
                    form_type=row[4],
                    processing_status=row[5],
                    error_message=row[6]
                )
                for row in rows
            ]
    
    def insert_form_template(self, template: Dict[str, Any]) -> int:
        """Insert a new form template."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO form_templates (name, description, extraction_fields, example_prompt, validation_rules)
                VALUES (?, ?, ?, ?, ?)
            """, (
                template["name"],
                template["description"],
                ",".join(template["extraction_fields"]),
                template.get("example_prompt", ""),
                str(template.get("validation_rules", {}))
            ))
            template_id = cursor.lastrowid
            conn.commit()
            return template_id
    
    def get_form_templates(self) -> List[Dict[str, Any]]:
        """Get all form templates."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM form_templates")
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "extraction_fields": row[3].split(",") if row[3] else [],
                    "example_prompt": row[4],
                    "validation_rules": eval(row[5]) if row[5] else {}
                }
                for row in rows
            ]
    
    def close(self):
        """Close database connection."""
        pass  # SQLite connections are automatically closed
