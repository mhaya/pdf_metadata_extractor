"""Ollama API client for LLM-based metadata extraction."""

import json

import ollama

from .models import LLMMetadata, LLMStats


SYSTEM_PROMPT_AUTO = """Extract bibliographic metadata from the given document text.
Write all output values in the same language as the document.
Use null for fields not found in the text. The summary must not be empty."""

SYSTEM_PROMPT_LANG = """Extract bibliographic metadata from the given document text.
Write all output values in {language}.
Use null for fields not found in the text. The summary must not be empty."""

FEW_SHOT_USER = """Deep Learning for Natural Language Processing
John Smith, Jane Doe
Department of Computer Science, MIT
Published in: Journal of AI Research, Vol.15, No.3, pp.101-115, 2023
DOI: 10.1234/jair.2023.001
Abstract: This paper presents a novel approach to NLP using transformer architectures..."""

FEW_SHOT_ASSISTANT = json.dumps({
    "title": "Deep Learning for Natural Language Processing",
    "author": "John Smith, Jane Doe",
    "journal": "Journal of AI Research",
    "volume": "15",
    "number": "3",
    "pages": "101-115",
    "year": "2023",
    "doi": "10.1234/jair.2023.001",
    "summary": "This paper presents a novel approach to NLP using transformer architectures. The authors demonstrate improved performance on multiple benchmarks.",
    "keywords": ["deep learning", "NLP", "transformer", "natural language processing"],
    "category": "Academic",
    "language": "English",
}, ensure_ascii=False)

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": ["string", "null"]},
        "author": {"type": ["string", "null"]},
        "journal": {"type": ["string", "null"]},
        "volume": {"type": ["string", "null"]},
        "number": {"type": ["string", "null"]},
        "pages": {"type": ["string", "null"]},
        "year": {"type": ["string", "null"]},
        "doi": {"type": ["string", "null"]},
        "summary": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "category": {"type": "string"},
        "language": {"type": "string"},
    },
    "required": [
        "title", "author", "journal", "volume", "number", "pages",
        "year", "doi", "summary", "keywords", "category", "language",
    ],
}


def extract_llm_metadata(
    text: str, model: str = "llama3.2", language: str | None = None, debug: bool = False,
) -> LLMMetadata:
    """Extract metadata from text using LLM.

    Args:
        text: Document text to analyze.
        model: Ollama model name to use.
        debug: Whether to print debug information to stderr.

    Returns:
        LLMMetadata object with extracted information.

    Raises:
        ConnectionError: If Ollama server is not available.
        ValueError: If LLM response cannot be parsed.
    """
    if not text.strip():
        raise ValueError("Empty text provided for LLM analysis")

    if language:
        system_prompt = SYSTEM_PROMPT_LANG.format(language=language)
    else:
        system_prompt = SYSTEM_PROMPT_AUTO

    if debug:
        import sys
        print(f"[DEBUG] Model: {model}", file=sys.stderr)
        print(f"[DEBUG] Output language: {language or 'auto'}", file=sys.stderr)
        print(f"[DEBUG] System prompt: {system_prompt}", file=sys.stderr)
        print(f"[DEBUG] Few-shot example included: yes", file=sys.stderr)
        print(f"[DEBUG] Input text length: {len(text)} chars", file=sys.stderr)
        print(f"[DEBUG] Input text (first 500 chars):", file=sys.stderr)
        print(text[:500], file=sys.stderr)
        print("---", file=sys.stderr)

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": FEW_SHOT_USER},
                {"role": "assistant", "content": FEW_SHOT_ASSISTANT},
                {"role": "user", "content": text},
            ],
            format=JSON_SCHEMA,
            options={
                "temperature": 0.3,
            },
        )
    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            raise ConnectionError(
                f"Model '{model}' not found. Please run: ollama pull {model}"
            ) from e
        raise ConnectionError(f"Ollama API error: {e}") from e
    except Exception as e:
        if "connection" in str(e).lower() or "refused" in str(e).lower():
            raise ConnectionError(
                "Cannot connect to Ollama. Please ensure Ollama is running: ollama serve"
            ) from e
        raise

    response_text = response.message.content or ""

    # Extract LLM performance statistics
    prompt_tokens = getattr(response, "prompt_eval_count", 0) or 0
    output_tokens = getattr(response, "eval_count", 0) or 0
    prompt_eval_duration_ns = getattr(response, "prompt_eval_duration", 0) or 0
    eval_duration_ns = getattr(response, "eval_duration", 0) or 0
    total_duration_ns = getattr(response, "total_duration", 0) or 0

    # Convert nanoseconds to milliseconds
    prompt_eval_duration_ms = prompt_eval_duration_ns / 1_000_000
    eval_duration_ms = eval_duration_ns / 1_000_000
    total_duration_ms = total_duration_ns / 1_000_000

    # Calculate tokens per second
    prompt_tokens_per_sec = (
        prompt_tokens / (prompt_eval_duration_ns / 1_000_000_000)
        if prompt_eval_duration_ns > 0 else 0.0
    )
    output_tokens_per_sec = (
        output_tokens / (eval_duration_ns / 1_000_000_000)
        if eval_duration_ns > 0 else 0.0
    )

    llm_stats = LLMStats(
        model=model,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        prompt_eval_duration_ms=round(prompt_eval_duration_ms, 2),
        eval_duration_ms=round(eval_duration_ms, 2),
        total_duration_ms=round(total_duration_ms, 2),
        prompt_tokens_per_sec=round(prompt_tokens_per_sec, 2),
        output_tokens_per_sec=round(output_tokens_per_sec, 2),
    )

    if debug:
        import sys
        print(f"\n[DEBUG] Raw LLM response:", file=sys.stderr)
        print(response_text, file=sys.stderr)
        print("---", file=sys.stderr)
        print(f"[DEBUG] LLM Stats: {llm_stats.model_dump_json(indent=2)}", file=sys.stderr)

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {e}") from e

    if debug:
        import sys
        print(f"\n[DEBUG] Parsed JSON keys: {list(data.keys())}", file=sys.stderr)
        print(f"[DEBUG] Parsed JSON: {json.dumps(data, ensure_ascii=False, indent=2)}", file=sys.stderr)

    keywords = data.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",")]

    return LLMMetadata(
        title=data.get("title") or None,
        author=data.get("author") or None,
        journal=data.get("journal") or None,
        volume=data.get("volume") or None,
        number=data.get("number") or None,
        pages=data.get("pages") or None,
        year=data.get("year") or None,
        doi=data.get("doi") or None,
        summary=data.get("summary", ""),
        keywords=keywords,
        category=data.get("category", "Unknown"),
        language=data.get("language", "Unknown"),
        stats=llm_stats,
    )
