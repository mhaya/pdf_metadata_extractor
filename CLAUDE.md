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
├── cli.py            # CLI (argparse) with --debug, --model, --no-llm, --output, --language options
├── extractor.py      # Main orchestration (extract_file_properties + extract_text + LLM)
├── llm_client.py     # Ollama chat API with few-shot prompting + JSON schema enforcement
├── models.py         # Pydantic models (FileProperties, LLMMetadata, LLMStats, PDFMetadata)
└── pdf_parser.py     # PDF text extraction with PyMuPDF (sort=True for correct reading order)
```

## CLI Usage

### Basic Usage

```bash
uv run python -m pdf_metadata_extractor <pdf_file>
```

### CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `text` | Output format: `text` (human-readable) or `json` |
| `--model` | `-m` | `llama3.2` | Ollama model name to use |
| `--language` | `-l` | auto | Output language for extracted fields (e.g., `English`, `Japanese`) |
| `--no-llm` | | false | Skip LLM extraction, only show file properties |
| `--debug` | | false | Show debug output (intermediate data to stderr) |

### Examples

```bash
# Basic extraction with default model (llama3.2)
uv run python -m pdf_metadata_extractor paper.pdf

# Output as JSON
uv run python -m pdf_metadata_extractor paper.pdf --output json

# Use a different model (gemma3:12b for better Japanese support)
uv run python -m pdf_metadata_extractor paper.pdf --model gemma3:12b

# Force output language to English
uv run python -m pdf_metadata_extractor paper.pdf --language English

# Only extract file properties (no LLM)
uv run python -m pdf_metadata_extractor paper.pdf --no-llm

# Debug mode (shows prompts, raw LLM response, etc.)
uv run python -m pdf_metadata_extractor paper.pdf --debug
```

## Output Format

### Text Output (default)

```
==================================================
PDF Metadata
==================================================

[Document Metadata]
  Title:        Deep Learning for NLP
  Author:       John Smith, Jane Doe
  Journal:      Journal of AI Research
  Volume:       15
  Number:       3
  Pages:        101-115
  Year:         2023
  DOI:          10.1234/jair.2023.001
  Language:     English
  Category:     Academic
  Keywords:     deep learning, NLP, transformer

  Summary:
    This paper presents a novel approach...

[File Properties]
  Pages:        12
  File Size:    1.5 MB
  PDF Version:  PDF 1.7
  Created:      2023-01-15 10:30:00
  Modified:     2023-01-20 14:22:00

[LLM Statistics]
  Model:              llama3.2
  Prompt Tokens:      1234
  Output Tokens:      256
  Total Tokens:       1490
  Prompt Eval:        150.00 ms (8.23 tokens/sec)
  Output Generation:  500.00 ms (0.51 tokens/sec)
  Total Duration:     650.00 ms

==================================================
```

### JSON Output

```json
{
  "file": {
    "page_count": 12,
    "file_size": 1572864,
    "pdf_version": "PDF 1.7",
    "created_at": "2023-01-15T10:30:00",
    "modified_at": "2023-01-20T14:22:00"
  },
  "llm": {
    "title": "Deep Learning for NLP",
    "author": "John Smith, Jane Doe",
    "journal": "Journal of AI Research",
    "volume": "15",
    "number": "3",
    "pages": "101-115",
    "year": "2023",
    "doi": "10.1234/jair.2023.001",
    "summary": "This paper presents a novel approach...",
    "keywords": ["deep learning", "NLP", "transformer"],
    "category": "Academic",
    "language": "English",
    "stats": {
      "model": "llama3.2",
      "prompt_tokens": 1234,
      "output_tokens": 256,
      "total_tokens": 1490,
      "prompt_eval_duration_ms": 150.0,
      "eval_duration_ms": 500.0,
      "total_duration_ms": 650.0,
      "prompt_tokens_per_sec": 8.23,
      "output_tokens_per_sec": 0.51
    }
  }
}
```

## Data Models

### FileProperties
Physical properties extracted from PDF file (no LLM required).

| Field | Type | Description |
|-------|------|-------------|
| `page_count` | `int` | Number of pages |
| `file_size` | `int` | File size in bytes |
| `pdf_version` | `str \| None` | PDF version (e.g., "PDF 1.7") |
| `created_at` | `datetime \| None` | Creation timestamp |
| `modified_at` | `datetime \| None` | Last modification timestamp |

### LLMMetadata
Bibliographic metadata extracted by LLM analysis.

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str \| None` | Document title |
| `author` | `str \| None` | Author name(s) |
| `journal` | `str \| None` | Journal/conference name |
| `volume` | `str \| None` | Volume number |
| `number` | `str \| None` | Issue number |
| `pages` | `str \| None` | Page range (e.g., "101-115") |
| `year` | `str \| None` | Publication year |
| `doi` | `str \| None` | DOI identifier |
| `summary` | `str` | Document summary (required) |
| `keywords` | `list[str]` | Keywords/tags |
| `category` | `str` | Document category (e.g., "Academic", "Technical Report") |
| `language` | `str` | Document language |
| `stats` | `LLMStats \| None` | LLM performance statistics |

### LLMStats
Performance statistics from LLM inference.

| Field | Type | Description |
|-------|------|-------------|
| `model` | `str` | Model name used |
| `prompt_tokens` | `int` | Input token count |
| `output_tokens` | `int` | Output token count |
| `total_tokens` | `int` | Total tokens (prompt + output) |
| `prompt_eval_duration_ms` | `float` | Prompt evaluation time (ms) |
| `eval_duration_ms` | `float` | Output generation time (ms) |
| `total_duration_ms` | `float` | Total processing time (ms) |
| `prompt_tokens_per_sec` | `float` | Prompt processing speed |
| `output_tokens_per_sec` | `float` | Output generation speed |

### PDFMetadata
Combined result containing both file properties and LLM metadata.

| Field | Type | Description |
|-------|------|-------------|
| `file` | `FileProperties` | Physical file properties |
| `llm` | `LLMMetadata \| None` | LLM-extracted metadata (None if `--no-llm`) |

## Programmatic API

```python
from pdf_metadata_extractor import extract_metadata, PDFMetadata

# Basic usage
metadata: PDFMetadata = extract_metadata("paper.pdf")

# With options
metadata = extract_metadata(
    pdf_path="paper.pdf",
    use_llm=True,           # Set False to skip LLM
    model="gemma3:12b",     # Ollama model name
    language="Japanese",    # Output language (None for auto-detect)
    debug=False,            # Print debug info to stderr
)

# Access results
print(metadata.file.page_count)      # 12
print(metadata.llm.title)            # "Deep Learning for NLP"
print(metadata.llm.summary)          # "This paper presents..."
print(metadata.model_dump_json())    # Full JSON output
```

## LLM Utilization Techniques

This tool employs several techniques to improve LLM extraction quality:

### 1. Few-Shot Prompting

Instead of zero-shot prompting, the tool provides one complete example of input/output before the actual document text. This helps the LLM understand the expected format and field semantics.

```python
messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": FEW_SHOT_USER},        # Example input
    {"role": "assistant", "content": FEW_SHOT_ASSISTANT},  # Example output
    {"role": "user", "content": actual_document_text},  # Actual input
]
```

The few-shot example includes a realistic academic paper header with all fields populated, teaching the LLM:
- Which fields to extract (title, author, journal, volume, number, pages, year, DOI)
- Expected format for each field (e.g., pages as "101-115", DOI with prefix)
- How to write a concise summary
- How to identify keywords and category

### 2. JSON Schema Enforcement

The tool uses Ollama's `format` parameter to enforce a strict JSON schema on LLM output. This ensures:
- All required fields are present
- Field types are correct (string, array, null)
- No extraneous fields in output

```python
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": ["string", "null"]},
        "summary": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        ...
    },
    "required": ["title", "author", ..., "summary", "keywords", "category", "language"],
}

response = ollama.chat(model=model, messages=messages, format=JSON_SCHEMA)
```

### 3. Low Temperature Setting

Temperature is set to 0.3 to reduce randomness and improve consistency:

```python
options={"temperature": 0.3}
```

This balances:
- Consistency: Same document produces similar results across runs
- Flexibility: Enough variation to handle diverse document formats

### 4. Automatic Language Detection

By default, the system prompt instructs the LLM to output in the same language as the document:

```
Extract bibliographic metadata from the given document text.
Write all output values in the same language as the document.
```

This ensures Japanese papers get Japanese summaries/keywords, etc.

The `--language` option overrides this for explicit language control:

```
Write all output values in {language}.
```

### 5. Optimized Text Extraction

Text is extracted with `sort=True` in PyMuPDF to maintain proper reading order:

```python
page_text = page.get_text(sort=True)
```

This ensures title and author information (typically at the top) appear first in the extracted text, making them easier for the LLM to identify.

### 6. Configurable Text Limits

To balance extraction quality with LLM context limits:

```python
def extract_text(pdf_path, max_pages=50, max_chars=50000):
```

- **max_pages=50**: Covers most academic papers completely
- **max_chars=50000**: Prevents context overflow while capturing sufficient content for accurate summarization

### 7. Graceful Null Handling

The system prompt explicitly instructs: "Use null for fields not found in the text."

This prevents the LLM from hallucinating missing information while the JSON schema allows nullable fields for optional metadata.

### 8. Robust Keyword Parsing

The tool handles both array and comma-separated string formats for keywords:

```python
keywords = data.get("keywords", [])
if isinstance(keywords, str):
    keywords = [k.strip() for k in keywords.split(",")]
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
