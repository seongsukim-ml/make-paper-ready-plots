#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Validate a static PNG/PDF figure pair.")
    parser.add_argument("png", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--font-substring", default="")
    parser.add_argument("--min-width", type=int, default=1000)
    parser.add_argument("--min-height", type=int, default=500)
    return parser.parse_args()


def main():
    args = parse_args()
    with Image.open(args.png) as image:
        width, height = image.size
        image.verify()
    if width < args.min_width or height < args.min_height:
        raise ValueError(f"PNG is unexpectedly small: {width}x{height}")

    pdf_bytes = args.pdf.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("PDF signature is missing")
    pages = len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))
    if pages != 1:
        raise ValueError(f"Expected one PDF page, found {pages}")
    if args.font_substring and args.font_substring.encode() not in pdf_bytes:
        raise ValueError(f"PDF does not contain font substring {args.font_substring!r}")

    print(f"PNG: {width}x{height}, verified")
    print(f"PDF: {len(pdf_bytes)} bytes, {pages} page, verified")


if __name__ == "__main__":
    main()
