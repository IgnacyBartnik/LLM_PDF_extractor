"""
Pydantic schemas for data validation and structure.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ExtractionConfig(BaseModel):
    """Configuration for data extraction."""
    
    form_type: str = Field(..., description="Type of form being processed")
    extraction_fields: List[str] = Field(..., description="List of fields to extract")
    model_name: str = Field(default="gpt-5-nano", description="OpenAI model to use")
    temperature: float = Field(default=1, description="Model temperature for extraction")
    max_completion_tokens: int = Field(default=1000, description="Maximum tokens for response")


class FormMetadata(BaseModel):
    """Metadata about the uploaded form."""
    
    id: Optional[int] = Field(None, description="Database ID")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.now, description="Upload timestamp")
    form_type: str = Field(..., description="Detected or specified form type")
    processing_status: str = Field(default="pending", description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


class ExtractedData(BaseModel):
    """Extracted data from PDF forms."""
    
    id: Optional[int] = Field(None, description="Database ID")
    form_id: int = Field(..., description="Reference to form metadata")
    field_name: str = Field(..., description="Name of the extracted field")
    field_value: str = Field(..., description="Extracted value")
    confidence_score: Optional[float] = Field(None, description="Confidence in extraction")
    extraction_date: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    raw_text: Optional[str] = Field(None, description="Raw text used for extraction")


class ExtractionResult(BaseModel):
    """Complete result of an extraction process."""
    
    form_metadata: FormMetadata
    extracted_data: List[ExtractedData]
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class FormTypeTemplate(BaseModel):
    """Template for different form types."""
    
    name: str = Field(..., description="Form type name")
    description: str = Field(..., description="Form description")
    extraction_fields: List[str] = Field(..., description="Fields to extract")
    example_prompt: str = Field(..., description="Example extraction prompt")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
