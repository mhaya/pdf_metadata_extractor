"""Main extraction orchestration."""

from pathlib import Path

from .models import PDFMetadata
from .pdf_parser import extract_file_properties, extract_text
from .llm_client import extract_llm_metadata


def extract_metadata(
    pdf_path: str | Path,
    use_llm: bool = True,
    model: str = "llama3.2",
    language: str | None = None,
    debug: bool = False,
) -> PDFMetadata:
    """Extract metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file.
        use_llm: Whether to use LLM for advanced metadata extraction.
        model: Ollama model name to use for LLM extraction.
        language: Output language for all extracted fields (None = auto-detect).
        debug: Whether to print debug information to stderr.

    Returns:
        PDFMetadata object containing all extracted metadata.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a valid PDF.
        ConnectionError: If LLM is requested but Ollama is not available.
    """
    pdf_path = Path(pdf_path)

    # Extract physical file properties
    file_properties = extract_file_properties(pdf_path)

    if debug:
        import sys
        print(f"[DEBUG] File properties: {file_properties.model_dump_json(indent=2)}", file=sys.stderr)

    # Extract LLM metadata if requested
    llm_metadata = None
    if use_llm:
        text = extract_text(pdf_path)
        if debug:
            import sys
            print(f"\n[DEBUG] Extracted text length: {len(text)} chars", file=sys.stderr)
        if text.strip():
            llm_metadata = extract_llm_metadata(text, model=model, language=language, debug=debug)

    return PDFMetadata(
        file=file_properties,
        llm=llm_metadata,
    )
