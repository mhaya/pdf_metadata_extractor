"""Pydantic data models for PDF metadata."""

from datetime import datetime
from pydantic import BaseModel


class FileProperties(BaseModel):
    """Physical properties of the PDF file."""

    page_count: int
    file_size: int
    pdf_version: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None


class LLMStats(BaseModel):
    """LLM performance statistics."""

    model: str
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    prompt_eval_duration_ms: float
    eval_duration_ms: float
    total_duration_ms: float
    prompt_tokens_per_sec: float
    output_tokens_per_sec: float


class LLMMetadata(BaseModel):
    """Metadata extracted by LLM analysis."""

    title: str | None = None
    author: str | None = None
    journal: str | None = None
    volume: str | None = None
    number: str | None = None
    pages: str | None = None
    year: str | None = None
    doi: str | None = None
    summary: str
    keywords: list[str]
    category: str
    language: str
    stats: LLMStats | None = None


class PDFMetadata(BaseModel):
    """Combined PDF metadata."""

    file: FileProperties
    llm: LLMMetadata | None = None
