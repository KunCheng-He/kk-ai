#!/usr/bin/env python3
"""Convert various file formats to Markdown using Microsoft MarkItDown.

Supports: PDF, Word, PowerPoint, Excel, Images, HTML, CSV, JSON, XML,
EPUB, ZIP, Audio, YouTube URLs, and more.

Usage:
    uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py document.pdf
"""

import argparse
import sys
from pathlib import Path


def convert_file(file_path: Path, output_dir: Path) -> Path:
    from markitdown import MarkItDown

    file_name = file_path.stem
    conversion_dir = output_dir / file_name
    conversion_dir.mkdir(parents=True, exist_ok=True)

    md_path = conversion_dir / f"{file_name}.md"

    md = MarkItDown()
    result = md.convert(str(file_path.resolve()))
    text = result.text_content

    if not text or not text.strip():
        print(
            f"Warning: Conversion produced empty output."
            f" The file may be unsupported, corrupted, or require additional dependencies.",
            file=sys.stderr,
        )

    md_path.write_text(text, encoding="utf-8")
    return md_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert files to Markdown using Microsoft MarkItDown"
    )
    parser.add_argument("file", help="Path to the file to convert")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="markdown-conversions",
        help="Parent directory for conversion output (default: markdown-conversions)",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)

    print(f"Converting: {file_path}")
    print(f"Output directory: {output_dir.resolve() / file_path.stem}")

    try:
        md_path = convert_file(file_path, output_dir)
    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone!")
    print(f"Markdown: {md_path.resolve()}")


if __name__ == "__main__":
    main()
