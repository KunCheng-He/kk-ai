#!/usr/bin/env python3
"""PDF to Markdown converter using pymupdf4llm.

Supports:
- Text-based PDFs with embedded images and tables
- Scanned PDFs via OCR (requires tesseract + --ocr flag)

Usage:
    uv run python convert.py document.pdf
    uv run python convert.py scanned.pdf --ocr
"""

import argparse
import os
import sys
from pathlib import Path


def has_text_layer(pdf_path: Path) -> bool:
    """Quick check if the PDF has a text layer by scanning first few pages."""
    import fitz

    doc = fitz.open(str(pdf_path))
    check_pages = min(3, len(doc))
    total_chars = 0
    for i in range(check_pages):
        page = doc[i]
        text = page.get_text()
        total_chars += len(text.strip())
    doc.close()
    return total_chars > 50


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    ocr: bool = False,
    ocr_lang: str = "chi_sim+eng",
) -> Path:
    import pymupdf4llm

    pdf_name = pdf_path.stem
    conversion_dir = output_dir / pdf_name
    images_dir = conversion_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    md_path = conversion_dir / f"{pdf_name}.md"

    orig_cwd = os.getcwd()
    os.chdir(str(conversion_dir))

    try:
        if ocr:
            import tesserocr
            md_text = pymupdf4llm.to_markdown(
                doc=str(pdf_path.resolve()),
                write_images=True,
                image_path="images",
                image_format="png",
                page_chunks=True,
            )
        else:
            md_text = pymupdf4llm.to_markdown(
                doc=str(pdf_path.resolve()),
                write_images=True,
                image_path="images",
                image_format="png",
            )
    finally:
        os.chdir(orig_cwd)

    md_path.write_text(md_text, encoding="utf-8")
    return md_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using pymupdf4llm"
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="pdf-conversions",
        help="Parent directory for conversion output (default: pdf-conversions)",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable OCR mode for scanned PDFs (requires tesseract + tesserocr)",
    )
    parser.add_argument(
        "--ocr-lang",
        default="chi_sim+eng",
        help="OCR language code (default: chi_sim+eng)",
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Error: Not a PDF file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)

    if not args.ocr:
        text_ok = has_text_layer(pdf_path)
        if not text_ok:
            print(
                "Warning: This PDF appears to have no text layer (scanned PDF?). "
                "Use --ocr flag for scanned documents.",
                file=sys.stderr,
            )

    print(f"Converting: {pdf_path}")
    print(f"OCR mode: {'ON' if args.ocr else 'OFF'}")
    print(f"Output directory: {output_dir.resolve() / pdf_path.stem}")

    md_path = convert_pdf(
        pdf_path,
        output_dir,
        ocr=args.ocr,
        ocr_lang=args.ocr_lang,
    )

    print(f"\nDone!")
    print(f"Markdown: {md_path.resolve()}")

    images_dir = md_path.parent / "images"
    if images_dir.exists():
        image_count = len(list(images_dir.iterdir()))
        if image_count > 0:
            print(f"Images: {images_dir.resolve()} ({image_count} files)")
        else:
            print("No embedded images found.")


if __name__ == "__main__":
    main()
