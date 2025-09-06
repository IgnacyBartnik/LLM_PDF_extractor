"""
PDF processing service for text extraction.
"""

import pypdf as PyPDF2  # modern replacement for PyPDF2
import logging
from typing import Optional, Tuple
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

    def extract_text(self, file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from a PDF file while preserving layout blocks.
        
        Returns:
            (success, text_content, error_message)
        """
        try:
            if not self.is_supported_file(file_path):
                return False, "", "Unsupported file type"

            doc = fitz.open(file_path)
            if len(doc) == 0:
                return False, "", "PDF file appears to be empty or corrupted"

            text_content = []
            for page_num, page in enumerate(doc, start=1):
                try:
                    # Get text in block mode (each block is a paragraph/table cell/etc.)
                    blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, text, block_no, block_type)
                    page_text = []
                    for b in sorted(blocks, key=lambda b: (b[1], b[0])):  # sort by y0, then x0
                        text = b[4].strip()
                        if text:
                            page_text.append(text)
                    
                    if page_text:
                        text_content.append(f"\n--- Page {page_num} ---\n" + "\n".join(page_text))
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue

            if not text_content:
                return False, "", "No text content could be extracted from PDF"

            result = "\n".join(text_content).strip()
            logger.info(f"Successfully extracted text ({len(result)} characters)")
            return True, result, None

        except Exception as e:
            error_msg = f"Unexpected error processing PDF: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
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