"""CLI entry point using argparse."""

import argparse
import json
import sys
from pathlib import Path

from .extractor import extract_metadata
from .models import PDFMetadata


def format_text_output(metadata: PDFMetadata) -> str:
    """Format metadata as human-readable text."""
    lines = []

    lines.append("=" * 50)
    lines.append("PDF Metadata")
    lines.append("=" * 50)

    # LLM-extracted metadata
    if metadata.llm:
        lines.append("\n[Document Metadata]")
        llm = metadata.llm

        if llm.title:
            lines.append(f"  Title:        {llm.title}")
        if llm.author:
            lines.append(f"  Author:       {llm.author}")
        if llm.journal:
            lines.append(f"  Journal:      {llm.journal}")
        if llm.volume:
            lines.append(f"  Volume:       {llm.volume}")
        if llm.number:
            lines.append(f"  Number:       {llm.number}")
        if llm.pages:
            lines.append(f"  Pages:        {llm.pages}")
        if llm.year:
            lines.append(f"  Year:         {llm.year}")
        if llm.doi:
            lines.append(f"  DOI:          {llm.doi}")
        lines.append(f"  Language:     {llm.language}")
        lines.append(f"  Category:     {llm.category}")
        lines.append(f"  Keywords:     {', '.join(llm.keywords)}")
        lines.append(f"\n  Summary:")
        for line in wrap_text(llm.summary, width=45, indent="    "):
            lines.append(line)

    # File properties
    lines.append("\n[File Properties]")
    fp = metadata.file

    lines.append(f"  Pages:        {fp.page_count}")
    lines.append(f"  File Size:    {format_file_size(fp.file_size)}")
    if fp.pdf_version:
        lines.append(f"  PDF Version:  {fp.pdf_version}")
    if fp.created_at:
        lines.append(f"  Created:      {fp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    if fp.modified_at:
        lines.append(f"  Modified:     {fp.modified_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # LLM Statistics
    if metadata.llm and metadata.llm.stats:
        stats = metadata.llm.stats
        lines.append("\n[LLM Statistics]")
        lines.append(f"  Model:              {stats.model}")
        lines.append(f"  Prompt Tokens:      {stats.prompt_tokens}")
        lines.append(f"  Output Tokens:      {stats.output_tokens}")
        lines.append(f"  Total Tokens:       {stats.total_tokens}")
        lines.append(f"  Prompt Eval:        {stats.prompt_eval_duration_ms:.2f} ms ({stats.prompt_tokens_per_sec:.2f} tokens/sec)")
        lines.append(f"  Output Generation:  {stats.eval_duration_ms:.2f} ms ({stats.output_tokens_per_sec:.2f} tokens/sec)")
        lines.append(f"  Total Duration:     {stats.total_duration_ms:.2f} ms")

    lines.append("\n" + "=" * 50)

    return "\n".join(lines)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def wrap_text(text: str, width: int = 70, indent: str = "") -> list[str]:
    """Wrap text to specified width."""
    words = text.split()
    lines = []
    current_line = indent

    for word in words:
        if len(current_line) + len(word) + 1 <= width + len(indent):
            if current_line == indent:
                current_line += word
            else:
                current_line += " " + word
        else:
            lines.append(current_line)
            current_line = indent + word

    if current_line.strip():
        lines.append(current_line)

    return lines


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="pdf-metadata-extractor",
        description="Extract metadata from PDF files using Llama via Ollama",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to the PDF file",
    )

    parser.add_argument(
        "-o",
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "-m",
        "--model",
        default="llama3.2",
        help="Ollama model name (default: llama3.2)",
    )

    parser.add_argument(
        "-l",
        "--language",
        default=None,
        help="Output language for all extracted fields (e.g., English, Japanese). Default: auto-detect from PDF",
    )

    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM extraction (only show file properties)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug output (intermediate data to stderr)",
    )

    args = parser.parse_args()

    # Validate file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not args.file.suffix.lower() == ".pdf":
        print(f"Warning: File may not be a PDF: {args.file}", file=sys.stderr)

    try:
        metadata = extract_metadata(
            pdf_path=args.file,
            use_llm=not args.no_llm,
            model=args.model,
            language=args.language,
            debug=args.debug,
        )

        if args.output == "json":
            print(metadata.model_dump_json(indent=2))
        else:
            print(format_text_output(metadata))

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
