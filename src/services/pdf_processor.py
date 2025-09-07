"""
PDF processing service for text extraction.
"""

import pypdf as PyPDF2  # modern replacement for PyPDF2
import logging
from typing import Optional, Tuple, Dict
from pathlib import Path
import io

import fitz  # PyMuPDF




logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF file processing and text extraction (layout-aware)."""

    def __init__(self):
        self.supported_extensions = {".pdf"}

    def is_supported_file(self, filename: str) -> bool:
        return Path(filename).suffix.lower() in self.supported_extensions

    def extract_text_and_tables(self, file_path: str):
        """
        Extract text and tables from a PDF file.
        Returns:
            (success, text_content, tables, error_message)
        """
        try:
            if not self.is_supported_file(file_path):
                return False, "", [], "Unsupported file type"

            doc = fitz.open(file_path)
            if len(doc) == 0:
                return False, "", [], "PDF file appears to be empty or corrupted"

            text_content = []
            for page_num, page in enumerate(doc, start=1):
                try:
                    blocks = page.get_text("blocks")
                    page_text = []
                    for b in sorted(blocks, key=lambda b: (b[1], b[0])):
                        text = b[4].strip()
                        if text:
                            page_text.append(text)
                    if page_text:
                        text_content.append(f"\n--- Page {page_num} ---\n" + "\n".join(page_text))
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue

            # Table extraction using camelot
            try:
                import camelot
                tables = camelot.read_pdf(file_path, pages="all")
                extracted_tables = [t.df for t in tables]
                logger.info(f"Extracted {len(extracted_tables)} tables from PDF.")
            except Exception as e:
                logger.warning(f"Table extraction failed: {e}")
                extracted_tables = []

            if not text_content and not extracted_tables:
                return False, "", [], "No text or tables could be extracted from PDF"

            result = "\n".join(text_content).strip()
            logger.info(f"Successfully extracted text ({len(result)} characters) and {len(extracted_tables)} tables.")
            return True, result, extracted_tables, None

        except Exception as e:
            error_msg = f"Unexpected error processing PDF: {e}"
            logger.error(error_msg)
            return False, "", [], error_msg

    # For backward compatibility
    def extract_text(self, file_path: str):
        """
        Extract text and tables, but return only text for legacy calls.
        """
        success, text, tables, error = self.extract_text_and_tables(file_path)
        return success, text, error
    
    def get_pdf_info(self, file_content: bytes) -> Tuple[bool, Dict, Optional[str]]:
        """
        Get basic information about the PDF file.
        
        Returns:
            (success, info_dict, error_message)
        """
        try:
            pdf_file = io.BytesIO(file_content)
            doc = fitz.open(stream=pdf_file, filetype="pdf")

            info = {
                "num_pages": len(doc),
                "file_size": len(file_content),
                "metadata": doc.metadata or {},
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
            (is_valid, error_message)
        """
        # Size checks before parsing
        if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
            return False, "PDF file is too large (max 50MB)"
        if len(file_content) < 100:  # 100 bytes minimum
            return False, "PDF file is too small"

        try:
            pdf_file = io.BytesIO(file_content)
            doc = fitz.open(stream=pdf_file, filetype="pdf")

            # Check if PDF has at least one page
            if len(doc) == 0:
                return False, "PDF file has no pages"

            return True, None

        except Exception as e:
            return False, f"PDF validation failed: {str(e)}"