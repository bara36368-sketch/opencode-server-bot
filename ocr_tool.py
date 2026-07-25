#!/usr/bin/env python3
"""
OCR Tool - Extract text from images using easyocr or tesseract.
Usage: python ocr_tool.py <image_path> [--output output.txt] [--lang en]
"""
import sys, os, argparse

def ocr_easyocr(image_path, langs=None):
    import easyocr
    reader = easyocr.Reader(langs or ['en'], gpu=False)
    results = reader.readtext(image_path)
    lines = []
    for (bbox, text, conf) in results:
        lines.append(text)
    return "\n".join(lines)

def ocr_tesseract(image_path, lang='eng'):
    import pytesseract
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang=lang)

def main():
    parser = argparse.ArgumentParser(description="OCR: Extract text from images")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--output", "-o", help="Write result to file")
    parser.add_argument("--lang", default="en", help="Language (default: en)")
    parser.add_argument("--engine", choices=["easyocr", "tesseract"], default="easyocr")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"ERROR: File not found: {args.image}")
        sys.exit(1)

    print(f"Running OCR on: {args.image} (engine: {args.engine})")
    try:
        if args.engine == "easyocr":
            text = ocr_easyocr(args.image, [args.lang])
        else:
            text = ocr_tesseract(args.image, args.lang)
    except Exception as e:
        print(f"OCR failed: {type(e).__name__}: {e}")
        sys.exit(1)

    print("=" * 60)
    print(text)
    print("=" * 60)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved to: {args.output}")

if __name__ == "__main__":
    main()
