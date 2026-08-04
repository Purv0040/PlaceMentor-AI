"""Module 1: PDF Text Extraction Service.

Uses PyMuPDF (fitz) as primary parser with pdfplumber as a fallback parser.
Validates empty, corrupted, or encrypted PDFs.
Returns extracted plain text and page count.
"""

import io
from typing import Union, Tuple
import fitz  # PyMuPDF
import pdfplumber

from utils.exceptions import InvalidPDFError, EmptyResumeError
from utils.logger import logger, log_execution_time


class PDFParserService:
    """Service to parse and extract text from PDF files using PyMuPDF & pdfplumber."""

    @log_execution_time
    def extract_text_and_page_count(self, pdf_input: Union[bytes, str, io.BytesIO]) -> Tuple[str, int]:
        """Extract plain text and page count from PDF bytes or path.

        Args:
            pdf_input: Raw bytes, file path, or BytesIO stream of the PDF.

        Returns:
            Tuple of (extracted_text_string, page_count_int).

        Raises:
            InvalidPDFError: If PDF is encrypted, corrupt, or unreadable.
            EmptyResumeError: If no text could be extracted.
        """
        pdf_bytes = self._get_bytes(pdf_input)
        if not pdf_bytes or len(pdf_bytes) == 0:
            raise EmptyResumeError("PDF file input is empty (0 bytes).")

        extracted_text = ""
        page_count = 1

        # Primary Parser: PyMuPDF (fitz)
        try:
            extracted_text, page_count = self._parse_with_pymupdf(pdf_bytes)
            logger.info(f"Successfully parsed PDF using PyMuPDF (fitz). Pages: {page_count}.")
        except InvalidPDFError as exc:
            raise exc
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}. Attempting fallback to pdfplumber...")

        # Fallback Parser: pdfplumber if PyMuPDF returned little or no text
        if not extracted_text or len(extracted_text.strip()) < 20:
            try:
                extracted_text, page_count = self._parse_with_pdfplumber(pdf_bytes)
                logger.info(f"Successfully parsed PDF using fallback pdfplumber. Pages: {page_count}.")
            except Exception as e:
                logger.error(f"Fallback pdfplumber extraction failed: {e}")
                if not extracted_text:
                    raise InvalidPDFError("Failed to parse PDF content with both PyMuPDF and pdfplumber.")

        cleaned = extracted_text.strip()
        if not cleaned:
            raise EmptyResumeError("The PDF document contains no readable text. It may be scanned, encrypted, or image-only.")

        return cleaned, max(page_count, 1)

    def extract_text(self, pdf_input: Union[bytes, str, io.BytesIO]) -> str:
        """Backward-compatible extract_text method returning text string."""
        text, _ = self.extract_text_and_page_count(pdf_input)
        return text

    def _get_bytes(self, pdf_input: Union[bytes, str, io.BytesIO]) -> bytes:
        """Convert input to bytes stream."""
        if isinstance(pdf_input, bytes):
            return pdf_input
        elif isinstance(pdf_input, io.BytesIO):
            return pdf_input.getvalue()
        elif isinstance(pdf_input, str):
            with open(pdf_input, "rb") as f:
                return f.read()
        else:
            raise InvalidPDFError("Invalid input type provided for PDF parsing.")

    def _parse_with_pymupdf(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """Extract text and page count using PyMuPDF."""
        text_parts = []
        page_count = 1
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if doc.is_encrypted:
                raise InvalidPDFError("The PDF document is encrypted or password-protected.")

            page_count = len(doc)
            for page in doc:
                text_parts.append(page.get_text("text"))

            doc.close()
        except fitz.FileDataError:
            raise InvalidPDFError("Corrupted or invalid PDF file format.")
        except InvalidPDFError:
            raise
        except Exception as e:
            raise RuntimeError(f"PyMuPDF error: {e}")

        return "\n".join(text_parts), page_count

    def _parse_with_pdfplumber(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """Extract text and page count using pdfplumber."""
        text_parts = []
        page_count = 1
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts), page_count


# Singleton Service Instance
pdf_parser_service = PDFParserService()
