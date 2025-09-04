"""
Main extraction service that orchestrates PDF processing and AI extraction.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.schemas import (
    FormMetadata, 
    ExtractedData, 
    ExtractionConfig, 
    ExtractionResult
)
from ..models.database import DatabaseManager
from .pdf_processor import PDFProcessor
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class ExtractionService:
    """Main service for orchestrating PDF data extraction."""
    
    def __init__(self, db_manager: DatabaseManager, openai_service: OpenAIService):
        """Initialize extraction service."""
        self.db_manager = db_manager
        self.openai_service = openai_service
        self.pdf_processor = PDFProcessor()
        
        # Initialize default form templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default form templates in the database."""
        try:
            existing_templates = self.db_manager.get_form_templates()
            if not existing_templates:
                default_templates = [
                    {
                        "name": "Customer Registration",
                        "description": "General customer registration forms",
                        "extraction_fields": ["customer_name", "email", "phone", "address", "date_of_birth"],
                        "example_prompt": "Extract customer registration information from the form",
                        "validation_rules": {}
                    },
                    {
                        "name": "Insurance Claim",
                        "description": "Insurance claim forms (FNOL, property loss, etc.)",
                        "extraction_fields": ["claim_number", "policy_number", "claim_type", "incident_date", "damage_description"],
                        "example_prompt": "Extract insurance claim details from the form",
                        "validation_rules": {}
                    },
                    {
                        "name": "Loan Application",
                        "description": "Loan and mortgage application forms",
                        "extraction_fields": ["applicant_name", "loan_amount", "loan_type", "income", "employment_status"],
                        "example_prompt": "Extract loan application information from the form",
                        "validation_rules": {}
                    }
                ]
                
                for template in default_templates:
                    self.db_manager.insert_form_template(template)
                
                logger.info("Default form templates initialized")
        except Exception as e:
            logger.error(f"Failed to initialize default templates: {e}")
    
    def process_pdf_file(
        self, 
        file_content: bytes, 
        filename: str,
        extraction_config: ExtractionConfig
    ) -> ExtractionResult:
        """
        Process a PDF file and extract data.
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            extraction_config: Configuration for extraction
            
        Returns:
            ExtractionResult with processing results
        """
        start_time = time.time()
        
        try:
            # Validate PDF file
            is_valid, validation_error = self.pdf_processor.validate_pdf(file_content)
            if not is_valid:
                return ExtractionResult(
                    form_metadata=FormMetadata(
                        filename=filename,
                        file_size=len(file_content),
                        form_type=extraction_config.form_type,
                        processing_status="failed",
                        error_message=validation_error
                    ),
                    extracted_data=[],
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=validation_error
                )
            
            # Create form metadata
            form_metadata = FormMetadata(
                filename=filename,
                file_size=len(file_content),
                form_type=extraction_config.form_type,
                processing_status="processing"
            )
            
            # Insert form into database
            form_id = self.db_manager.insert_form(form_metadata)
            form_metadata.id = form_id
            
            # Extract text from PDF
            text_success, extracted_text, text_error = self.pdf_processor.extract_text(file_content)
            if not text_success:
                self.db_manager.update_form_status(form_id, "failed", text_error)
                return ExtractionResult(
                    form_metadata=form_metadata,
                    extracted_data=[],
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=text_error
                )
            
            # Use AI to extract structured data
            ai_result = self.openai_service.extract_data_from_text(
                text=extracted_text,
                extraction_fields=extraction_config.extraction_fields,
                form_type=extraction_config.form_type,
                model=extraction_config.model_name,
                temperature=extraction_config.temperature
            )
            
            if not ai_result.get("success", False):
                error_msg = ai_result.get("error", "AI extraction failed")
                self.db_manager.update_form_status(form_id, "failed", error_msg)
                return ExtractionResult(
                    form_metadata=form_metadata,
                    extracted_data=[],
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=error_msg
                )
            
            # Convert AI results to ExtractedData objects
            extracted_data_list = []
            extracted_data = ai_result.get("extracted_data", {})
            confidence_scores = ai_result.get("confidence_scores", {})
            reasoning = ai_result.get("reasoning", {})
            
            for field_name in extraction_config.extraction_fields:
                field_value = extracted_data.get(field_name, "Not found")
                confidence = confidence_scores.get(field_name, 0.0)
                field_reasoning = reasoning.get(field_name, "")
                
                extracted_data_obj = ExtractedData(
                    form_id=form_id,
                    field_name=field_name,
                    field_value=str(field_value),
                    confidence_score=confidence,
                    raw_text=field_reasoning
                )
                extracted_data_list.append(extracted_data_obj)
            
            # Store extracted data in database
            self.db_manager.insert_extracted_data(extracted_data_list)
            
            # Update form status to completed
            self.db_manager.update_form_status(form_id, "completed")
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully processed PDF {filename} in {processing_time:.2f}s")
            
            return ExtractionResult(
                form_metadata=form_metadata,
                extracted_data=extracted_data_list,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during processing: {str(e)}"
            logger.error(error_msg)
            
            # Update form status if we have a form_id
            if 'form_id' in locals():
                self.db_manager.update_form_status(form_id, "failed", error_msg)
            
            return ExtractionResult(
                form_metadata=FormMetadata(
                    filename=filename,
                    file_size=len(file_content),
                    form_type=extraction_config.form_type,
                    processing_status="failed",
                    error_message=error_msg
                ),
                extracted_data=[],
                processing_time=time.time() - start_time,
                success=False,
                error_message=error_msg
            )
    
    def get_extraction_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get extraction history with extracted data."""
        try:
            forms = self.db_manager.get_all_forms(limit=limit)
            history = []
            
            for form in forms:
                extracted_data = self.db_manager.get_extracted_data_by_form_id(form.id)
                history.append({
                    "form": form,
                    "extracted_data": extracted_data,
                    "data_count": len(extracted_data)
                })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get extraction history: {e}")
            return []
    
    def get_form_templates(self) -> List[Dict[str, Any]]:
        """Get available form templates."""
        try:
            return self.db_manager.get_form_templates()
        except Exception as e:
            logger.error(f"Failed to get form templates: {e}")
            return []
    
    def create_custom_template(
        self, 
        name: str, 
        description: str, 
        extraction_fields: List[str],
        example_prompt: str = "",
        validation_rules: Dict[str, Any] = None
    ) -> bool:
        """Create a custom form template."""
        try:
            template = {
                "name": name,
                "description": description,
                "extraction_fields": extraction_fields,
                "example_prompt": example_prompt,
                "validation_rules": validation_rules or {}
            }
            
            self.db_manager.insert_form_template(template)
            logger.info(f"Created custom template: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom template: {e}")
            return False
    
    def validate_extraction_config(self, config: ExtractionConfig) -> Tuple[bool, List[str]]:
        """Validate extraction configuration."""
        errors = []
        
        if not config.form_type:
            errors.append("Form type is required")
        
        if not config.extraction_fields:
            errors.append("At least one extraction field is required")
        
        if config.temperature < 0 or config.temperature > 2:
            errors.append("Temperature must be between 0 and 2")
        
        if config.max_tokens < 100 or config.max_tokens > 4000:
            errors.append("Max tokens must be between 100 and 4000")
        
        return len(errors) == 0, errors
