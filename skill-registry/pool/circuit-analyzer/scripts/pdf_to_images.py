#!/usr/bin/env python3
"""Convert circuit PDF to PNG images for Claude Vision analysis.

Usage:
    python pdf_to_images.py <pdf_path> [-d DPI] [-o OUTPUT_DIR] [--pages 1-3]
"""

import fitz  # PyMuPDF
import sys
import os
import json
import argparse


def pdf_to_images(pdf_path, dpi=200, output_dir=None, page_range=None):
    doc = fitz.open(pdf_path)
    output_dir = output_dir or os.path.join(
        os.environ.get('TEMP', '/tmp'), 'circuit_pages'
    )
    os.makedirs(output_dir, exist_ok=True)

    # Parse page range
    pages_to_render = set()
    if page_range:
        for part in page_range.split(','):
            if '-' in part:
                start, end = part.split('-', 1)
                pages_to_render.update(range(int(start), int(end) + 1))
            else:
                pages_to_render.add(int(part))
    else:
        pages_to_render = set(range(1, doc.page_count + 1))

    results = []
    for i, page in enumerate(doc):
        page_num = i + 1
        if page_num not in pages_to_render:
            continue
        pix = page.get_pixmap(dpi=dpi)
        out_path = os.path.join(output_dir, f'page_{page_num:03d}.png')
        pix.save(out_path)
        results.append({
            'page': page_num,
            'path': os.path.abspath(out_path),
            'width': pix.width,
            'height': pix.height,
        })

    output = {
        'source': os.path.abspath(pdf_path),
        'total_pages': doc.page_count,
        'rendered': len(results),
        'dpi': dpi,
        'pages': results,
    }
    print(json.dumps(output, indent=2))
    doc.close()


def main():
    parser = argparse.ArgumentParser(description='Convert circuit PDF to images')
    parser.add_argument('pdf_path', help='PDF file path')
    parser.add_argument('-d', '--dpi', type=int, default=200, help='DPI (default: 200)')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('--pages', help='Page range (e.g., 1-3 or 1,3,5)')
    args = parser.parse_args()

    pdf_to_images(args.pdf_path, args.dpi, args.output, args.pages)


if __name__ == '__main__':
    main()
