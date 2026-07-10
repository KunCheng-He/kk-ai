#!/usr/bin/env python3
"""Convert various file formats to Markdown using Microsoft MarkItDown.

Supports: PDF, Word, PowerPoint, Excel, Images, HTML, CSV, JSON, XML,
EPUB, ZIP, Audio, YouTube URLs, and more.

Usage:
    uv run --project <skill-path>/scripts python <skill-path>/scripts/convert.py document.pdf
"""

import argparse
import os
import sys
import time
from pathlib import Path

VERSION = "1.1.0"

SKILL_SCRIPTS_DIR = Path(__file__).resolve().parent


def check_gitignore(output_dir: Path) -> None:
    """Warn if the output directory is not in .gitignore."""
    project_root = output_dir.resolve().parent
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return
    content = gitignore.read_text(encoding="utf-8")
    dir_name = output_dir.name + "/"
    if dir_name not in content and output_dir.name not in content.splitlines():
        print(
            f"\033[33mWarning: '{output_dir.name}/' not found in {gitignore}.\n"
            f"Consider adding it to avoid committing temporary conversion files.\033[0m",
            file=sys.stderr,
        )


def needs_conversion(file_path: Path, md_path: Path) -> bool:
    """Return True if the source file is newer than the output (or output doesn't exist)."""
    if not md_path.exists():
        return True
    src_mtime = file_path.stat().st_mtime
    out_mtime = md_path.stat().st_mtime
    return src_mtime > out_mtime


def convert_file(
    file_path: Path,
    output_dir: Path,
    use_llm: bool = False,
    llm_model: str | None = None,
) -> Path:
    from markitdown import MarkItDown

    file_name = file_path.stem
    conversion_dir = output_dir / file_name
    conversion_dir.mkdir(parents=True, exist_ok=True)

    md_path = conversion_dir / f"{file_name}.md"

    if not needs_conversion(file_path, md_path):
        print(f"Skipping (already converted and up to date): {md_path}")
        return md_path

    convert_kwargs = {}
    if use_llm:
        convert_kwargs["use_llm"] = True
        if llm_model:
            convert_kwargs["llm_model"] = llm_model

    md = MarkItDown()
    result = md.convert(str(file_path.resolve()), **convert_kwargs)
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
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable LLM-based OCR via markitdown-ocr plugin (requires markitdown[llm-image])",
    )
    parser.add_argument(
        "--llm-model",
        help="LLM model for OCR (e.g. gpt-4o, claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force re-conversion even if output is up to date",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"files-to-markdown v{VERSION}",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        candidates = list(Path.cwd().glob(f"*{file_path.name}*"))
        hint = ""
        if candidates:
            hint = f"\nDid you mean one of these?\n" + "\n".join(
                f"  {c}" for c in candidates[:5]
            )
        print(f"Error: File not found: {file_path}{hint}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    check_gitignore(output_dir)

    print(f"Converting: {file_path}")
    print(f"Output directory: {output_dir.resolve() / file_path.stem}")

    # Override needs_conversion with force flag
    if args.force:
        global needs_conversion
        needs_conversion = lambda fp, mp: True

    try:
        md_path = convert_file(
            file_path,
            output_dir,
            use_llm=args.ocr,
            llm_model=args.llm_model,
        )
    except ModuleNotFoundError as e:
        print(
            f"Error: Missing dependency: {e}\n"
            f"Run: cd {SKILL_SCRIPTS_DIR} && uv sync\n"
            f"If using OCR: uv sync --extra llm-image",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e)
        suggestion = ""

        if "api_key" in err_msg.lower() or "apikey" in err_msg.lower():
            suggestion = (
                "Set OPENAI_API_KEY environment variable for audio transcription."
            )
        elif "permission" in err_msg.lower():
            suggestion = "Check file permissions and try again."
        elif "memory" in err_msg.lower() or "timeout" in err_msg.lower():
            suggestion = (
                "The file may be too large. Try a smaller file or split the document."
            )

        print(f"Error: {err_type}: {err_msg}", file=sys.stderr)
        if suggestion:
            print(f"  Suggestion: {suggestion}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone!")
    print(f"Markdown: {md_path.resolve()}")


if __name__ == "__main__":
    main()
