# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Metadata Extractor - A CLI tool that extracts bibliographic metadata from PDF files using LLM via Ollama.

## Tech Stack

- **Language**: Python 3.10+
- **Package Manager**: uv
- **PDF Parsing**: PyMuPDF (fitz)
- **LLM Client**: ollama (chat API with JSON schema)
- **Data Models**: Pydantic v2

## Project Structure

```
pdf_metadata_extractor/
├── __init__.py       # Package exports (FileProperties, LLMMetadata, PDFMetadata, extract_metadata)
├── __main__.py       # Module entry point
├── cli.py            # CLI (argparse) with --debug, --model, --no-llm, --output options
├── extractor.py      # Main orchestration (extract_file_properties + extract_text + LLM)
├── llm_client.py     # Ollama chat API with few-shot prompting + JSON schema enforcement
├── models.py         # Pydantic models (FileProperties, LLMMetadata, PDFMetadata)
└── pdf_parser.py     # PDF text extraction with PyMuPDF (sort=True for correct reading order)
```

## Common Commands

```bash
# Install dependencies
uv sync

# Run the tool
uv run python -m pdf_metadata_extractor <pdf_file>

# Run with options
uv run python -m pdf_metadata_extractor <pdf_file> --output json
uv run python -m pdf_metadata_extractor <pdf_file> --no-llm
uv run python -m pdf_metadata_extractor <pdf_file> --model gemma3:12b
uv run python -m pdf_metadata_extractor <pdf_file> --debug
```

## Architecture Notes

### Data Flow
1. `cli.py` parses command-line arguments
2. `extractor.py` orchestrates the extraction process
3. `pdf_parser.py` extracts file properties (page count, size, dates) and full text using PyMuPDF
4. `llm_client.py` sends text to Ollama chat API with few-shot example and JSON schema
5. Results are formatted and output as text or JSON

### Key Design Decisions
- All content metadata (title, author, journal, summary, keywords, etc.) is extracted by LLM
- PDF parsing only extracts text and physical file properties (page count, file size, dates, PDF version)
- Text extraction uses `sort=True` in PyMuPDF to ensure correct reading order (title/author first)
- Text extraction covers full document (50 pages / 50000 chars limit) for accurate summarization
- LLM uses `ollama.chat()` with system/user messages and few-shot example for better instruction following
- JSON schema is passed via `format` parameter to enforce output structure
- LLM output language matches the PDF content language (auto-detected)
- Pydantic models provide type safety and serialization

### Models
- `FileProperties`: page_count, file_size, pdf_version, created_at, modified_at
- `LLMMetadata`: title, author, journal, volume, number, pages, year, doi, summary, keywords, category, language
- `PDFMetadata`: file (FileProperties) + llm (optional LLMMetadata)

### Error Handling
- `FileNotFoundError`: PDF file not found
- `ValueError`: Invalid PDF or unparseable LLM response
- `ConnectionError`: Ollama server not running or model not found

## Dependencies

Defined in `pyproject.toml`, locked in `uv.lock`:
- pymupdf>=1.24.0
- ollama>=0.3.0
- pydantic>=2.0

## Prerequisites

- Ollama must be running: `ollama serve`
- Model must be downloaded: `ollama pull llama3.2`
- For better accuracy with Japanese documents: `ollama pull gemma3:12b`
