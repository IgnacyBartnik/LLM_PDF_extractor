"""
Tests for PDF processor service.
"""

import pytest
import io
from unittest.mock import Mock, patch
from services.pdf_processor import PDFProcessor


class TestPDFProcessor:
    """Test cases for PDFProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
    
    def test_is_supported_file(self):
        """Test file type validation."""
        assert self.processor.is_supported_file("test.pdf") == True
        assert self.processor.is_supported_file("test.PDF") == True
        assert self.processor.is_supported_file("test.txt") == False
        assert self.processor.is_supported_file("test.docx") == False
    
    def test_validate_pdf_valid_file(self):
        """Test PDF validation with valid file."""
        # Create a minimal valid PDF content
        valid_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 10\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000111 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        
        is_valid, error = self.processor.validate_pdf(valid_pdf_content)
        assert is_valid == True
        assert error is None
    
    def test_validate_pdf_empty_file(self):
        """Test PDF validation with empty file."""
        empty_content = b""
        is_valid, error = self.processor.validate_pdf(empty_content)
        assert is_valid == False
        assert "too small" in error
    
    def test_validate_pdf_large_file(self):
        """Test PDF validation with oversized file."""
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        is_valid, error = self.processor.validate_pdf(large_content)
        assert is_valid == False
        assert "too large" in error
    
    @patch('PyPDF2.PdfReader')
    def test_extract_text_success(self, mock_pdf_reader):
        """Test successful text extraction."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text content"
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Test extraction
        success, text, error = self.processor.extract_text(b"fake_pdf_content")
        
        assert success == True
        assert "Sample text content" in text
        assert error is None
    
    @patch('PyPDF2.PdfReader')
    def test_extract_text_empty_pages(self, mock_pdf_reader):
        """Test text extraction with empty pages."""
        # Mock empty PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = []
        
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Test extraction
        success, text, error = self.processor.extract_text(b"fake_pdf_content")
        
        assert success == False
        assert text == ""
        assert "empty or corrupted" in error
    
    @patch('PyPDF2.PdfReader')
    def test_extract_text_multiple_pages(self, mock_pdf_reader):
        """Test text extraction from multiple pages."""
        # Mock multiple pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Test extraction
        success, text, error = self.processor.extract_text(b"fake_pdf_content")
        
        assert success == True
        assert "Page 1 content" in text
        assert "Page 2 content" in text
        assert "Page 1" in text
        assert "Page 2" in text
        assert error is None
    
    @patch('PyPDF2.PdfReader')
    def test_extract_text_page_error(self, mock_pdf_reader):
        """Test text extraction with page errors."""
        # Mock pages with one failing
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = Mock()
        mock_page2.extract_text.side_effect = Exception("Page error")
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Test extraction
        success, text, error = self.processor.extract_text(b"fake_pdf_content")
        
        assert success == True  # Should still succeed with partial extraction
        assert "Page 1 content" in text
        assert error is None
    
    @patch('PyPDF2.PdfReader')
    def test_get_pdf_info_success(self, mock_pdf_reader):
        """Test successful PDF info retrieval."""
        # Mock PDF reader with metadata
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
        mock_reader_instance.metadata = {"Title": "Test Document"}
        
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Test info retrieval
        success, info, error = self.processor.get_pdf_info(b"fake_pdf_content")
        
        assert success == True
        assert info["num_pages"] == 2
        assert info["metadata"]["Title"] == "Test Document"
        assert error is None
    
    def test_get_pdf_info_error(self):
        """Test PDF info retrieval with error."""
        # Test with invalid content
        success, info, error = self.processor.get_pdf_info(b"invalid_pdf_content")
        
        assert success == False
        assert info == {}
        assert error is not None


if __name__ == "__main__":
    pytest.main([__file__])
