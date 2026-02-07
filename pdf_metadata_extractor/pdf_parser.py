"""PDF parsing and text extraction using PyMuPDF."""

import os
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF

from .models import FileProperties


def parse_pdf_date(date_str: str | None) -> datetime | None:
    """Parse PDF date string to datetime object.

    PDF dates are typically in format: D:YYYYMMDDHHmmSS+HH'mm'
    """
    if not date_str:
        return None

    # Remove 'D:' prefix if present
    if date_str.startswith("D:"):
        date_str = date_str[2:]

    # Try common formats
    formats = [
        "%Y%m%d%H%M%S",
        "%Y%m%d%H%M%S%z",
        "%Y%m%d",
    ]

    # Clean up timezone info
    date_str = date_str.replace("'", "").replace("Z", "+0000")
    # Handle +HH'mm' format -> +HHmm
    if "+" in date_str:
        parts = date_str.split("+")
        if len(parts) == 2:
            date_str = parts[0][:14]  # Take only the date part

    for fmt in formats:
        try:
            return datetime.strptime(date_str[: len(fmt.replace("%", ""))], fmt)
        except (ValueError, IndexError):
            continue

    return None


def extract_file_properties(pdf_path: str | Path) -> FileProperties:
    """Extract physical file properties from PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        FileProperties object with extracted information.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a valid PDF.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    file_size = os.path.getsize(pdf_path)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Failed to open PDF: {e}") from e

    try:
        metadata = doc.metadata or {}

        pdf_version = None
        try:
            if doc.xref_length() > 0:
                pdf_version = f"{doc.metadata.get('format', 'PDF')}"
                if pdf_version == "PDF":
                    pdf_version = None
        except Exception:
            pass

        return FileProperties(
            page_count=doc.page_count,
            file_size=file_size,
            pdf_version=pdf_version,
            created_at=parse_pdf_date(metadata.get("creationDate")),
            modified_at=parse_pdf_date(metadata.get("modDate")),
        )
    finally:
        doc.close()


def extract_text(pdf_path: str | Path, max_pages: int = 50, max_chars: int = 50000) -> str:
    """Extract text from PDF for LLM analysis.

    Args:
        pdf_path: Path to the PDF file.
        max_pages: Maximum number of pages to extract (default: 50).
        max_chars: Maximum number of characters to return (default: 50000).

    Returns:
        Extracted text content.
    """
    pdf_path = Path(pdf_path)

    doc = fitz.open(pdf_path)
    try:
        text_parts = []
        total_chars = 0

        for page_num in range(min(max_pages, doc.page_count)):
            page = doc[page_num]
            page_text = page.get_text(sort=True)

            if total_chars + len(page_text) > max_chars:
                remaining = max_chars - total_chars
                text_parts.append(page_text[:remaining])
                break

            text_parts.append(page_text)
            total_chars += len(page_text)

        return "\n\n".join(text_parts)
    finally:
        doc.close()
