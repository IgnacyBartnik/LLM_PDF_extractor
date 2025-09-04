"""
PDF processing service for text extraction.
"""

import PyPDF2
import logging
from typing import Optional, Tuple
from pathlib import Path
import io

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    def __init__(self):
        """Initialize PDF processor."""
        self.supported_extensions = {'.pdf'}
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file type is supported."""
        return Path(filename).suffix.lower() in self.supported_extensions
    
    def extract_text(self, file_content: bytes) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from PDF file content.
        
        Returns:
            Tuple of (success, text_content, error_message)
        """
        try:
            # Create a BytesIO object from the file content
            pdf_file = io.BytesIO(file_content)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if not pdf_reader.pages:
                return False, "", "PDF file appears to be empty or corrupted"
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content.strip():
                return False, "", "No text content could be extracted from PDF"
            
            logger.info(f"Successfully extracted text from PDF ({len(text_content)} characters)")
            return True, text_content.strip(), None
            
        except PyPDF2.errors.PdfReadError as e:
            error_msg = f"PDF read error: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error processing PDF: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def get_pdf_info(self, file_content: bytes) -> Tuple[bool, dict, Optional[str]]:
        """
        Get basic information about the PDF file.
        
        Returns:
            Tuple of (success, info_dict, error_message)
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            info = {
                'num_pages': len(pdf_reader.pages),
                'file_size': len(file_content),
                'metadata': pdf_reader.metadata or {}
            }
            
            return True, info, None
            
        except Exception as e:
            error_msg = f"Error getting PDF info: {str(e)}"
            logger.error(error_msg)
            return False, {}, error_msg
    
    def validate_pdf(self, file_content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate PDF file for processing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF has pages
            if not pdf_reader.pages:
                return False, "PDF file has no pages"
            
            # Check file size (reasonable limits)
            if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
                return False, "PDF file is too large (max 50MB)"
            
            if len(file_content) < 100:  # 100 bytes minimum
                return False, "PDF file is too small"
            
            return True, None
            
        except Exception as e:
            return False, f"PDF validation failed: {str(e)}"
