import io
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PDFExtractionError(Exception):
    """Raised when PDF extraction fails or PDF is invalid."""
    pass

class ParserService:
    """Service for parsing documents."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extracts text from a PDF file using PyMuPDF.
        
        Args:
            pdf_bytes: The raw bytes of the PDF file.
            
        Returns:
            Extracted text as a string, with page boundaries preserved.
            
        Raises:
            PDFExtractionError: If the PDF is unreadable or empty.
        """
        if not pdf_bytes:
            raise PDFExtractionError("PDF data is empty.")
            
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            if doc.page_count == 0:
                raise PDFExtractionError("PDF contains no pages.")
                
            extracted_text = []
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if text.strip():
                    extracted_text.append(f"--- PAGE {page_num + 1} ---\n{text}")
                    
            doc.close()
            
            final_text = "\n\n".join(extracted_text).strip()
            
            if not final_text:
                raise PDFExtractionError("PDF contains no readable text. It might be an image-only PDF.")
                
            return final_text
            
        except PDFExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise PDFExtractionError(f"Failed to parse PDF: {str(e)}")
